import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const API_BASE = "http://localhost:8000";

function App() {
  const [assistants, setAssistants] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => uuidv4()); // Generar session_id único al cargar

  useEffect(() => {
    fetchAssistants();
  }, []);

  useEffect(() => {
    if (selectedId) {
      fetchDocuments();
      setMessages([]);
    }
  }, [selectedId]);

  const fetchAssistants = async () => {
    try {
      const res = await axios.get(`${API_BASE}/assistants`);
      setAssistants(res.data);
    } catch (err) {
      console.error("Error fetching assistants:", err);
    }
  };

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(`${API_BASE}/assistants/${selectedId}/documents`);
      setDocuments(res.data);
    } catch (err) {
      console.error("Error fetching documents:", err);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !selectedId) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await axios.post(
        `${API_BASE}/assistants/${selectedId}/documents`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      if (res.data.success) {
        alert(`✅ Documento cargado: ${res.data.chunks_indexed} chunks indexados`);
        fetchDocuments();
      } else {
        alert(`❌ Error: ${res.data.error}`);
      }
    } catch (err) {
      alert(`❌ Error al cargar: ${err.message}`);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const sendMessage = async () => {
    if (!input || !selectedId) return;
    const userMsg = { role: 'user', content: input };
    setMessages([...messages, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        assistant_id: selectedId,
        message: input,
        session_id: sessionId  // ← Enviando session_id
      });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div className="w-72 bg-slate-800 text-white p-4 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">🤖 Asistentes RAG</h2>
        <button className="w-full bg-blue-600 p-2 rounded mb-4 hover:bg-blue-700">+ Nuevo Asistente</button>
        
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">ASISTENTES</h3>
          <ul>
            {assistants.map(a => (
              <li 
                key={a.id} 
                onClick={() => setSelectedId(a.id)}
                className={`p-3 cursor-pointer rounded mb-1 transition ${selectedId === a.id ? 'bg-blue-500' : 'hover:bg-slate-700'}`}
              >
                <div className="font-semibold">{a.name}</div>
                <div className="text-xs text-gray-300">{a.description || "Sin descripción"}</div>
              </li>
            ))}
          </ul>
        </div>

        {selectedId && (
          <div className="border-t border-slate-600 pt-4">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">📄 DOCUMENTOS</h3>
            
            <label className="w-full bg-green-600 p-2 rounded mb-3 cursor-pointer hover:bg-green-700 inline-block text-center">
              {uploading ? "⏳ Cargando..." : "📥 Cargar PDF"}
              <input 
                type="file" 
                accept=".pdf" 
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>

            <div className="space-y-1">
              {documents.length > 0 ? (
                documents.map(doc => (
                  <div key={doc.id} className="p-2 bg-slate-700 rounded text-xs">
                    <div className="font-semibold truncate">{doc.filename}</div>
                    <div className="text-gray-400">{new Date(doc.created_at).toLocaleDateString()}</div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-gray-400 italic">Sin documentos</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        {selectedId ? (
          <>
            <div className="flex-1 p-6 overflow-y-auto bg-white">
              {messages.length === 0 ? (
                <div className="text-center text-gray-400 mt-20">
                  <p className="text-lg">Carga un PDF y comienza a preguntar ↓</p>
                </div>
              ) : (
                messages.map((m, i) => (
                  <div key={i} className={`mb-4 flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <span className={`inline-block p-3 rounded-lg max-w-md ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-900'}`}>
                      {m.content}
                    </span>
                  </div>
                ))
              )}
              {loading && <div className="text-center text-gray-400">⏳ Generando respuesta...</div>}
            </div>
            
            <div className="p-4 bg-white border-t flex gap-2">
              <input 
                className="flex-1 border p-2 rounded"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Pregunta algo al asistente..."
                disabled={loading}
              />
              <button 
                onClick={sendMessage} 
                disabled={loading || !input}
                className="bg-blue-600 text-white px-6 rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                Enviar
              </button>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <p className="text-lg">Selecciona un asistente para comenzar</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
