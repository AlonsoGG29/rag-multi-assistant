import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import { SmartToy as SmartToyIcon, Person as PersonIcon } from '@mui/icons-material';

export function ChatMessage({ message, index }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <Box
      key={index}
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        alignItems: 'flex-end',
        gap: 1,
        animation: 'fadeIn 0.3s ease-in-out',
      }}
    >
      {!isUser && (
        <Avatar
          sx={{
            bgcolor: isSystem ? '#fbbf24' : '#3b82f6',
            width: 32,
            height: 32,
            flexShrink: 0,
          }}
        >
          {isSystem ? 'ⓘ' : <SmartToyIcon sx={{ fontSize: 18 }} />}
        </Avatar>
      )}

      <Paper
        sx={{
          p: 1.5,
          maxWidth: '70%',
          minWidth: '100px',
          bgcolor: isUser ? '#2563eb' : isSystem ? '#fef3c7' : '#e5e7eb',
          color: isUser ? 'white' : isSystem ? '#92400e' : '#1f2937',
          borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap',
          boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
        }}
        elevation={0}
      >
        <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
          {message.content}
        </Typography>
      </Paper>

      {isUser && (
        <Avatar
          sx={{
            bgcolor: '#10b981',
            width: 32,
            height: 32,
            flexShrink: 0,
          }}
        >
          <PersonIcon sx={{ fontSize: 18 }} />
        </Avatar>
      )}
    </Box>
  );
}

export default ChatMessage;
