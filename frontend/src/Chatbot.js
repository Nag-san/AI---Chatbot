import React, { useState } from "react";
import axios from "axios";

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");

  const formatText = (text) => {
    if (!text) return "";

    return text.replace(/\n/g, "<br>");
  };

  const sendMessage = async () => {
    if (!query.trim()) return; //for empty queries

    const userMessage = { sender: "user", text: query };
    setMessages([...messages, userMessage]); //adding user query to messages

    try {
      //fetching bot reply
      const bodyquery = {
        query: "`${query}`",
      };
      const response = await axios.post("http://127.0.0.1:5000/query", {
        query,
      });
      const botText = response.data.summary
        ? response.data.summary
        : response.data.error
        ? response.data.error
        : "No summary available.";
      const botMessage = { sender: "bot", text: JSON.stringify(botText) };

      setMessages([...messages, userMessage, botMessage]); //adding bot reply to messages
    } catch (error) {
      console.error("Error fetching data:", error);
      const errorMessage = { sender: "bot", text: "Error processing query." };
      setMessages([...messages, errorMessage]);
    }

    setQuery(""); //clearing input field
  };

  return (
    <div style={styles.container}>
      <div style={styles.chatWidndow}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={
              msg.sender === "user" ? styles.userMessage : styles.botMessage
            }
            dangerouslySetInnerHTML={{ __html: msg.text }} //formatting message to print new lines
          />
        ))}
      </div>

      <div style={styles.inputContainer}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about products or suppliers..."
          style={styles.input}
        />

        <button onClick={sendMessage} style={styles.button}>
          {" "}
          Send{" "}
        </button>
      </div>
    </div>
  );
};

//CSS styling
const styles = {
  container: {
    width: "600px",
    margin: "auto",
    border: "1px solid #ccc",
    borderRadius: "5px",
    padding: "10px",
  },
  chatWidndow: {
    height: "800px",
    overflowY: "auto",
    padding: "10px",
    background: "#f5f5f5",
  },
  userMessage: {
    background: "#007bff",
    color: "#fff",
    padding: "8px",
    borderRadius: "5px",
    marginBottom: "5px",
    alignSelf: "flex-end",
  },
  botMessage: {
    background: "#ddd",
    padding: "8px",
    borderRadius: "5px",
    marginBottom: "5px",
    alignSelf: "flex-start",
  },
  inputContainer: { display: "flex", marginTop: "10px" },
  input: {
    flex: 1,
    padding: "8px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  },
  button: {
    background: "#007bff",
    color: "#fff",
    padding: "8px",
    marginLeft: "5px",
    cursor: "pointer",
  },
};

export default Chatbot;
