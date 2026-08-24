import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import io, { Socket } from 'socket.io-client';
import { useAuth } from './AuthContext'; // It's common for SocketContext to depend on AuthContext

// --- Define the shape of the context value ---
// This tells TypeScript what data and functions will be available.
interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
}

// --- Create the Context ---
// This creates the context object that components will subscribe to.
const SocketContext = createContext<SocketContextType | undefined>(undefined);

// --- Create a Custom Hook ---
// This is a helper hook that makes it easy for other components to get the socket info.
export const useSocket = () => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

// --- Create the Provider Component ---
// This is the main component that will wrap your app (or parts of it).
// It manages the actual socket connection.
export const SocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user } = useAuth(); // Get user from AuthContext to manage the connection
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // We only want to establish a socket connection if the user is logged in
    // and that user object actually contains a token.
    if (user && 'token' in user && (user as any).token) {
      // IMPORTANT: Use proxy instead of hardcoded URL
      const newSocket = io('/', {
        // Sending the auth token with the connection is a common pattern for authentication.
        // We use `(user as any)` here to bypass the TypeScript error, as our check above
        // already confirms the token exists. The ideal fix is in the AuthContext type definitions.
        auth: {
          token: (user as any).token
        }
      });

      setSocket(newSocket);

      // --- Set up event listeners ---
      newSocket.on('connect', () => {
        setIsConnected(true);
        console.log('Socket connected successfully:', newSocket.id);
      });

      newSocket.on('disconnect', () => {
        setIsConnected(false);
        console.log('Socket disconnected.');
      });

      // --- Clean up the connection ---
      // This function will be called when the component unmounts or when the user changes.
      // It's crucial for preventing memory leaks.
      return () => {
        newSocket.disconnect();
      };
    }
  }, [user]); // This effect re-runs whenever the user object changes.

  // The value that will be provided to all consuming components.
  const value = { socket, isConnected };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};
