import logging
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    metrics,
    RoomInputOptions,
)
from livekit.plugins import (
    google,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
import os


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
with open("instructions.txt", "r", encoding="utf-8") as f:
    instructions = f.read()

from livekit.agents import function_tool, RunContext
import httpx


@function_tool()
async def send_whatsapp_message(
    context: RunContext,
    mobile: str,
    msg: str,
) -> str:
    """
    Send a WhatsApp message to the given mobile number with the specified message and session ID.
    """
    url = os.getenv("WHATSAPP_URL")  # Replace with your actual endpoint
    payload = {
        "mobile": mobile,
        "msg": msg,
        "session": os.getenv("SESSION_NAME"),
    }
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            return f"WhatsApp message sent successfully to {mobile}."
    except httpx.HTTPError as e:
        return f"Failed to send WhatsApp message: {str(e)}"



class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=instructions,
            stt = deepgram.STT(
                punctuate=True,
                numerals=True,
                profanity_filter=True,
            ),
            llm= google.LLM(model="gemini-2.0-flash-001"),
            tts =  deepgram.TTS(),
            # use LiveKit's transformer-based turn detector
            turn_detection=MultilingualModel(),
            tools=[send_whatsapp_message]
        )

    async def on_enter(self):
        await self.session.generate_reply(allow_interruptions=True)


    async def on_user_message(self, message: str):
        print(f"[DEBUG] on_user_message called with: '{message}'")
        await self.session.generate_reply(f"Did you say: {message}?")
        exit_phrases = ["thank you", "bye", "that's all", "goodbye", "we're done"]
        if any(phrase in message.lower() for phrase in exit_phrases):
            print("[DEBUG] Exit phrase detected. Disconnecting.")
            await self.session.generate_reply("Okay, talk to you soon. Goodbye!")
            await self.session.disconnect()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    usage_collector = metrics.UsageCollector()

    # Log metrics and collect usage data
    def on_metrics_collected(agent_metrics: metrics.AgentMetrics):
        metrics.log_metrics(agent_metrics)
        usage_collector.collect(agent_metrics)

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        # minimum delay for endpointing, used when turn detector believes the user is done with their turn
        min_endpointing_delay=0.5,
        # maximum delay for endpointing, used when turn detector does not believe the user is done with their turn
        max_endpointing_delay=5.0,
    )

    # Trigger the on_metrics_collected function when metrics are collected
    session.on("metrics_collected", on_metrics_collected)

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # enable background voice & noise cancellation, powered by Krisp
            # included at no additional cost with LiveKit Cloud
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
