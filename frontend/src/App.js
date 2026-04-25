import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  Button,
  TextField,
  List,
  ListItemButton,
  ListItemText,
  CircularProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Stack,
  Avatar,
  LinearProgress,
  Tooltip,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Send as SendIcon,
  CloudUpload as CloudUploadIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  SmartToy as SmartToyIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ChatMessage, DocumentsList, ChatInput, EmptyState } from './components';

const API_BASE = "http://localhost:8000";

// Tema personalizado
const theme = createTheme({
  palette: {
    primary: {
      main: '#2563eb',
      light: '#3b82f6',
      dark: '#1d4ed8',
    },
    secondary: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    background: {
      default: '#f3f4f6',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: '8px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  const [assistants, setAssistants] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => uuidv4());
  const [mobileOpen, setMobileOpen] = useState(false);
  const [showNewAssistantDialog, setShowNewAssistantDialog] = useState(false);
  const [newAssistantName, setNewAssistantName] = useState("");
  const [newAssistantDesc, setNewAssistantDesc] = useState("");
  const [creatingAssistant, setCreatingAssistant] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchAssistants();
  }, []);

  useEffect(() => {
    if (selectedId) {
      fetchDocuments();
      setMessages([]);
    }
  }, [selectedId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchAssistants = async () => {
    try {
      const res = await axios.get(`${API_BASE}/assistants`);
      setAssistants(res.data);
      if (res.data.length > 0 && !selectedId) {
        setSelectedId(res.data[0].id);
      }
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
        setMessages(prev => [...prev, {
          role: 'system',
          content: `✅ Documento "${file.name}" cargado exitosamente con ${res.data.chunks_indexed} chunks indexados`
        }]);
        fetchDocuments();
      } else {
        setMessages(prev => [...prev, {
          role: 'system',
          content: `❌ Error: ${res.data.error}`
        }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ Error al cargar: ${err.message}`
      }]);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !selectedId) return;
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        assistant_id: selectedId,
        message: input,
        session_id: sessionId
      });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAssistant = async () => {
    if (!newAssistantName.trim()) {
      alert("Por favor ingresa un nombre para el asistente");
      return;
    }

    setCreatingAssistant(true);
    try {
      const res = await axios.post(`${API_BASE}/assistants`, {
        name: newAssistantName,
        description: newAssistantDesc
      });

      setAssistants(prev => [...prev, res.data]);
      setSelectedId(res.data.id);
      setNewAssistantName("");
      setNewAssistantDesc("");
      setShowNewAssistantDialog(false);

      setMessages(prev => [...prev, {
        role: 'system',
        content: `✅ Asistente "${newAssistantName}" creado exitosamente`
      }]);
    } catch (err) {
      alert(`Error al crear asistente: ${err.message}`);
    } finally {
      setCreatingAssistant(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar este PDF?")) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/assistants/${selectedId}/documents/${docId}`);
      setMessages(prev => [...prev, {
        role: 'system',
        content: '✅ PDF eliminado exitosamente'
      }]);
      fetchDocuments();
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ Error al eliminar PDF: ${err.message}`
      }]);
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const selectedAssistant = assistants.find(a => a.id === selectedId);

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: '#f8fafc' }}>
      {/* Header */}
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <SmartToyIcon />
          <Typography variant="h6">RAG Assistants</Typography>
        </Box>
        <Typography variant="caption" sx={{ opacity: 0.9 }}>
          Multi-Document AI Chat
        </Typography>
      </Box>

      {/* New Assistant Button */}
      <Box sx={{ p: 2 }}>
        <Button
          fullWidth
          variant="contained"
          color="secondary"
          startIcon={<SmartToyIcon />}
          onClick={() => setShowNewAssistantDialog(true)}
        >
          + Nuevo Asistente
        </Button>
      </Box>

      <Divider />

      {/* Assistants List */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
        <Typography variant="caption" sx={{ px: 2, display: 'block', color: 'text.secondary', mb: 1, fontWeight: 600 }}>
          ASISTENTES ({assistants.length})
        </Typography>
        <List sx={{ py: 0 }}>
          {assistants.map(a => (
            <ListItemButton
              key={a.id}
              selected={selectedId === a.id}
              onClick={() => {
                setSelectedId(a.id);
                setMobileOpen(false);
              }}
              sx={{
                borderRadius: '8px',
                mx: 1,
                mb: 0.5,
                '&.Mui-selected': {
                  bgcolor: 'primary.light',
                  color: 'white',
                  '&:hover': {
                    bgcolor: 'primary.main',
                  },
                },
              }}
            >
              <Avatar sx={{ width: 32, height: 32, mr: 1.5, bgcolor: 'primary.main', fontSize: '0.9rem' }}>
                {a.name.charAt(0).toUpperCase()}
              </Avatar>
              <ListItemText
                primary={a.name}
                secondary={a.description || "Sin descripción"}
                primaryTypographyProps={{ variant: 'body2', fontWeight: 600 }}
                secondaryTypographyProps={{
                  sx: {
                    color: selectedId === a.id ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                  }
                }}
              />
            </ListItemButton>
          ))}
        </List>
      </Box>

      <Divider />

      {/* Documents Section */}
      {selectedId && (
        <Box sx={{ p: 2, bgcolor: '#f8fafc' }}>
          <DocumentsList 
            documents={documents} 
            uploading={uploading}
            onFileUpload={handleFileUpload}
            onDeleteDocument={handleDeleteDocument}
          />
        </Box>
      )}
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default' }}>
        {/* Desktop Drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            width: 320,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 320,
              boxSizing: 'border-box',
              border: 'none',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Mobile Drawer */}
        <Drawer
          anchor="left"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              width: 280,
              boxSizing: 'border-box',
            },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Main Content */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* AppBar */}
          <AppBar 
            position="static" 
            elevation={1} 
            sx={{ 
              borderBottom: '1px solid #e5e7eb',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)'
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                edge="start"
                onClick={() => setMobileOpen(true)}
                sx={{ display: { md: 'none' }, mr: 2 }}
              >
                ☰
              </IconButton>
              
              {selectedAssistant ? (
                <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, gap: 1.5 }}>
                  <Avatar 
                    sx={{ 
                      bgcolor: 'rgba(255,255,255,0.2)', 
                      border: '2px solid rgba(255,255,255,0.3)',
                      width: 40,
                      height: 40,
                    }}
                  >
                    {selectedAssistant.name.charAt(0).toUpperCase()}
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                      {selectedAssistant.name}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.85 }}>
                      {selectedAssistant.description || 'Asistente IA'}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography variant="h6" sx={{ flex: 1, fontWeight: 700 }}>
                  RAG Multi-Assistant
                </Typography>
              )}

              <Tooltip title="Opciones">
                <IconButton color="inherit" onClick={handleMenuOpen}>
                  <MoreVertIcon />
                </IconButton>
              </Tooltip>
              
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
              >
                <MenuItem onClick={handleMenuClose}>
                  <SettingsIcon sx={{ mr: 1, fontSize: 20 }} /> 
                  Configuración
                </MenuItem>
                <MenuItem onClick={handleMenuClose}>
                  <LogoutIcon sx={{ mr: 1, fontSize: 20 }} /> 
                  Salir
                </MenuItem>
              </Menu>
            </Toolbar>
          </AppBar>

          {/* Chat Area */}
          {selectedId ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              {/* Messages */}
              <Box
                sx={{
                  flex: 1,
                  overflowY: 'auto',
                  p: 2,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 2,
                  bgcolor: '#fafbfc',
                }}
              >
                {messages.length === 0 ? (
                  <EmptyState 
                    icon={CloudUploadIcon}
                    title="Comienza una conversación"
                    subtitle="Carga un documento PDF y haz preguntas al asistente"
                  />
                ) : (
                  <>
                    {messages.map((m, i) => (
                      <ChatMessage key={i} message={m} index={i} />
                    ))}
                    {loading && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                          <SmartToyIcon sx={{ fontSize: 18 }} />
                        </Avatar>
                        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                          Generando respuesta...
                        </Typography>
                      </Box>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </Box>

              {loading && <LinearProgress sx={{ height: 3 }} />}

              {/* Área de Input */}
              <ChatInput 
                input={input}
                onInput={setInput}
                onSend={sendMessage}
                disabled={loading}
              />
            </Box>
          ) : (
            <EmptyState 
              icon={SmartToyIcon}
              title="Selecciona un asistente"
              subtitle="Elige un asistente del sidebar para comenzar a conversar"
            />
          )}
        </Box>

        {/* Diálogo Nuevo Asistente */}
        <Dialog 
          open={showNewAssistantDialog} 
          onClose={() => !creatingAssistant && setShowNewAssistantDialog(false)} 
          maxWidth="sm" 
          fullWidth
        >
          <DialogTitle sx={{ fontWeight: 700 }}>Crear Nuevo Asistente</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Nombre del Asistente"
                value={newAssistantName}
                onChange={(e) => setNewAssistantName(e.target.value)}
                placeholder="Ej: Abogado IA"
                disabled={creatingAssistant}
              />
              <TextField
                fullWidth
                label="Descripción"
                value={newAssistantDesc}
                onChange={(e) => setNewAssistantDesc(e.target.value)}
                multiline
                rows={3}
                placeholder="Descripción del asistente..."
                disabled={creatingAssistant}
              />
            </Stack>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button 
              onClick={() => setShowNewAssistantDialog(false)}
              disabled={creatingAssistant}
            >
              Cancelar
            </Button>
            <Button 
              variant="contained" 
              onClick={handleCreateAssistant}
              disabled={creatingAssistant}
            >
              {creatingAssistant ? <CircularProgress size={20} sx={{ mr: 1 }} /> : ''}
              Crear Asistente
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </ThemeProvider>
  );
}

export default App;