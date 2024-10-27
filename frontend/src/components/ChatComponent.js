import React, { useState, useEffect } from "react";
import { uploadImage, sendMessage, fetchDisasterInfo } from "../api/api";
import "./ChatComponent.css";

function ChatComponent() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [location, setLocation] = useState({ lat: null, lon: null });

    useEffect(() => {
        // Capture user location when the component mounts
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                setLocation({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                });
            });
        }
    }, []);

    const handleSendMessage = async () => {
        if (!input) return;
        
        const response = await sendMessage(input, location);
        setMessages([...messages, { role: "user", content: input }, { role: "assistant", content: response.reply }]);
        setInput("");
    };

    const handleFetchDisasterInfo = async () => {
        const response = await fetchDisasterInfo({ message: input, ...location });

        if (response.success) {
            setMessages([...messages, { role: "assistant", content: response.data.join("\n") }]);
        } else {
            setMessages([...messages, { role: "assistant", content: response.message }]);
        }
    };

    return (
        <div className="chat-fullscreen">
            <div className="chat-header">
                <h2>Chat with AI</h2>
            </div>

            <div className="chat-box">
                {messages.map((msg, idx) => (
                    <div key={idx} className={msg.role === "user" ? "message user-message" : "message assistant-message"}>
                        <p>{msg.content}</p>
                    </div>
                ))}
            </div>

            <div className="chat-input-section">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message here (e.g., Milton hurricane)..."
                    className="chat-input"
                />
                <button onClick={handleSendMessage} className="send-button">Send</button>
                <button onClick={handleFetchDisasterInfo} className="send-button">Get Disaster Info</button>
            </div>
        </div>
    );
}

export default ChatComponent;
