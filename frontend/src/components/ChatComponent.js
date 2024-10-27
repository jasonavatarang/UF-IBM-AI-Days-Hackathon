import React, { useState } from "react";
import { uploadImage, sendMessage } from "../api/api";
import "./ChatComponent.css";  // Import the CSS file for styling

function ChatComponent() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [file, setFile] = useState(null);

    const handleImageUpload = async () => {
        if (!file) return;
        const response = await uploadImage(file);
        setMessages([...messages, { role: "user", content: response.image_base64 }]);
    };

    const handleSendMessage = async () => {
        if (!input) return;
        const response = await sendMessage(input);
        setMessages([...messages, { role: "user", content: input }, { role: "assistant", content: response.reply }]);
        setInput("");
    };

    return (
        <div className="chat-fullscreen">
            <div className="chat-header">
                <h2>Chat with AI</h2>
            </div>

            <div className="chat-box">
                {messages.map((msg, idx) => (
                    <div key={idx} className={msg.role === "user" ? "message user-message" : "message assistant-message"}>
                        {msg.role === "user" && file ? (
                            <img src={`data:image/png;base64,${msg.content}`} alt="uploaded" className="uploaded-image" />
                        ) : (
                            <p>{msg.content}</p>
                        )}
                    </div>
                ))}
            </div>

            <div className="chat-input-section">
                <input type="file" onChange={(e) => setFile(e.target.files[0])} className="upload-input" />
                <button onClick={handleImageUpload} className="upload-button">Upload Image</button>

                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message here..."
                    className="chat-input"
                />
                <button onClick={handleSendMessage} className="send-button">Send</button>
            </div>
        </div>
    );
}

export default ChatComponent;
