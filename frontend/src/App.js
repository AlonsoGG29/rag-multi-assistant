import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = "http://localhost:8000";

function App() {
  const [assistants, setAssistants] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    fetchAssistants();
  }, []);

  const fetchAssistants = async () => {
    const res = await axios.get(`${API_BASE}/assistants`);
    setAssistants(res.data);
  };

  const sendMessage = async () => {
    if (!input || !selectedId) return;
    const userMsg = { role: 'user', content: input };
    setMessages([...messages, userMsg]);
    
    const res = await axios.post(`${API_BASE}/chat`, {
      assistant_id: selectedId,
      message: input
    });
    
    setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    setInput("");
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-slate-800 text-white p-4">
        <h2 className="text-xl font-bold mb-4">Asistentes RAG</h2>
        <button className="w-full bg-blue-600 p-2 rounded mb-4">+ Nuevo Asistente</button>
        <ul>
          {assistants.map(a => (
            <li 
              key={a.id} 
              onClick={() => setSelectedId(a.id)}
              className={`p-2 cursor-pointer rounded ${selectedId === a.id ? 'bg-blue-500' : 'hover:bg-slate-700'}`}
            >
              {a.name}
            </li>
          ))}
        </ul>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 p-6 overflow-y-auto">
          {messages.map((m, i) => (
            <div key={i} className={`mb-4 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
              <span className={`inline-block p-3 rounded-lg ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'}`}>
                {m.content}
              </span>
            </div>
          ))}
        </div>
        <div className="p-4 bg-white border-t flex">
          <input 
            className="flex-1 border p-2 rounded-l"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Pregunta algo al asistente..."
          />
          <button onClick={sendMessage} className="bg-blue-600 text-white px-6 rounded-r">Enviar</button>
        </div>
      </div>
    </div>
  );
}

export default App;
