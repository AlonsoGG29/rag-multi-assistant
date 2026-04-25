import React from 'react';
import { Box, Typography } from '@mui/material';

export function EmptyState({ icon: Icon, title, subtitle }) {
  return (
    <Box
      sx={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
        color: 'text.secondary',
      }}
    >
      <Icon sx={{ fontSize: 80, mb: 2, opacity: 0.15 }} />
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {subtitle}
      </Typography>
    </Box>
  );
}

export default EmptyState;
