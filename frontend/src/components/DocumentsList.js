import React from 'react';
import { Box, Stack, Paper, Typography, Button, Alert, CircularProgress, IconButton } from '@mui/material';
import { Description as DescriptionIcon, CloudUpload as CloudUploadIcon, Close as CloseIcon } from '@mui/icons-material';

export function DocumentsList({ documents, uploading, onFileUpload, onDeleteDocument }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase' }}>
        📄 Documentos ({documents.length})
      </Typography>

      <label htmlFor="file-upload" style={{ width: '100%' }}>
        <input
          id="file-upload"
          type="file"
          accept=".pdf"
          onChange={onFileUpload}
          disabled={uploading}
          style={{ display: 'none' }}
        />
        <Button
          component="span"
          fullWidth
          variant="contained"
          color="secondary"
          startIcon={uploading ? <CircularProgress size={18} /> : <CloudUploadIcon />}
          disabled={uploading}
        >
          {uploading ? 'Cargando...' : 'Cargar PDF'}
        </Button>
      </label>

      {documents.length > 0 ? (
        <Stack spacing={1}>
          {documents.map((doc, idx) => (
            <Paper
              key={doc.id || idx}
              sx={{
                p: 1.5,
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                bgcolor: 'background.paper',
                border: '1px solid #e0e7ff',
                borderRadius: '8px',
                transition: 'all 0.2s',
                '&:hover': {
                  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                  borderColor: '#3b82f6',
                },
              }}
              elevation={0}
            >
              <DescriptionIcon sx={{ color: 'primary.main', flexShrink: 0 }} />
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="caption" noWrap sx={{ fontWeight: 600, display: 'block' }}>
                  {doc.filename}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  {new Date(doc.created_at).toLocaleDateString('es-ES')}
                </Typography>
              </Box>
              <IconButton
                size="small"
                onClick={() => onDeleteDocument && onDeleteDocument(doc.id)}
                sx={{
                  color: '#ef4444',
                  '&:hover': {
                    bgcolor: '#fee2e2'
                  }
                }}
              >
                <CloseIcon sx={{ fontSize: 18 }} />
              </IconButton>
            </Paper>
          ))}
        </Stack>
      ) : (
        <Alert severity="info" icon={false} sx={{ fontSize: '0.75rem', py: 1 }}>
          Carga un PDF para comenzar
        </Alert>
      )}
    </Box>
  );
}

export default DocumentsList;
