import { useState } from "react";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");

  const runAI = async () => {
    try {
      const res = await fetch("https://api.opengradient.ai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // 🔥 IMPORTANT: yahan baad me API key aayegi
          Authorization: "Bearer YOUR_API_KEY"
        },
        body: JSON.stringify({
          model: "og-chat",
          messages: [
            { role: "user", content: prompt }
          ]
        })
      });

      const data = await res.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      console.error(err);
      setResult("Error running model");
    }
  };

  return (
    <div style={{ padding: 40 }}>
      <h1>🔥 OpenGradient AI Demo</h1>

      <textarea
        rows={4}
        style={{ width: "100%" }}
        placeholder="Ask OG model something..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <br /><br />

      <button onClick={runAI}>
        Run OpenGradient Model
      </button>

      <pre>{result}</pre>
    </div>
  );
}