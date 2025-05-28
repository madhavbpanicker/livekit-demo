import { useState, useCallback } from "react";
import { LivekitRoom, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";


const LivekitModal = ({ setShowSupport }) => {
    const [isSubmittingName, setIsSubmittingName] = useState(false);
    const [name, setName] = useState("");

    const handleNameSubmit = () => {};

    return <div className="modal-overlay">
        <div className='modal-content'>
            <div className='support-room'>
                ()
                 isSubmittingName ? (
                    <form onSubmit={ } className="name-form">
                        <h2>Enter your name to connect with support</h2>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Your Name"
                            required
                        />
                        <button type="submit" disabled={!name}>Join Support Room</button>
                    </form>
                 ) : ()
            </div>
        </div>
}