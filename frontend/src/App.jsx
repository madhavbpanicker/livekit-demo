import { useState } from 'react'
import './App.css'

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleSupportClick = () => {
    setShowSupport(true);
    // Here you can add logic to open a chat window or redirect to a support page
    console.log("Support button clicked");
  }
  return (
    <div className='app'>
      <header className='header'>
        <div className='logo'>Jade Cucine</div>
      </header>
      
      <main className='main'>
        <h1>Welcome to Jade Cucine</h1>
        <p>Your one-stop solution for kitchen design and renovation.</p>
        <button className='support-button' onClick={}>Talk to An Agent!</button>
      </main>
    </div>
  )
}

export default App
