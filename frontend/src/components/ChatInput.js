import React from 'react';
import { Paper, TextField, Button, Box } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

export function ChatInput({ input, onInput, onSend, disabled, placeholder = "Escribe tu pregunta..." }) {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <Paper
      sx={{
        p: 2,
        borderTop: '1px solid #e5e7eb',
        display: 'flex',
        gap: 1,
        bgcolor: 'background.paper',
      }}
      elevation={0}
    >
      <TextField
        fullWidth
        placeholder={placeholder}
        value={input}
        onChange={(e) => onInput(e.target.value)}
        onKeyPress={handleKeyPress}
        disabled={disabled}
        multiline
        maxRows={4}
        size="small"
        variant="outlined"
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: '8px',
            transition: 'all 0.2s',
            '&:hover': {
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            },
          },
        }}
      />
      <Button
        onClick={onSend}
        disabled={disabled || !input.trim()}
        variant="contained"
        color="primary"
        endIcon={<SendIcon />}
        sx={{ alignSelf: 'flex-end', whiteSpace: 'nowrap' }}
      >
        Enviar
      </Button>
    </Paper>
  );
}

export default ChatInput;
