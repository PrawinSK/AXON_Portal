import React, { createContext, useContext, useState, useEffect } from 'react';
import type { AuthUser, UserRole } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  loginStudent: (rollNumber: string, pass: string) => Promise<void>;
  loginStaff: (email: string, pass: string) => Promise<void>;
  loginHOD: (email: string, pass: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const saved = localStorage.getItem('axon_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('axon_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const verifyToken = async () => {
      const storedToken = localStorage.getItem('axon_token');
      if (!storedToken) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await api.getMe();
        if (me && me.sub) {
          // Valid token
          const restoredUser: AuthUser = {
            user_id: me.sub,
            name: me.name || 'User',
            role: me.role,
            department: me.department || 'Computer Science & Engineering',
            roll_number: me.roll_number,
            access_token: storedToken,
          };
          setUser(restoredUser);
          localStorage.setItem('axon_user', JSON.stringify(restoredUser));
        } else {
          logout();
        }
      } catch {
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    verifyToken();
  }, []);

  const loginStudent = async (rollNumber: string, pass: string) => {
    setIsLoading(true);
    try {
      const res = await api.loginStudent(rollNumber, pass);
      setUser(res);
      setToken(res.access_token);
      localStorage.setItem('axon_user', JSON.stringify(res));
    } finally {
      setIsLoading(false);
    }
  };

  const loginStaff = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const res = await api.loginStaff(email, pass);
      setUser(res);
      setToken(res.access_token);
      localStorage.setItem('axon_user', JSON.stringify(res));
    } finally {
      setIsLoading(false);
    }
  };

  const loginHOD = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const res = await api.loginHOD(email, pass);
      setUser(res);
      setToken(res.access_token);
      localStorage.setItem('axon_user', JSON.stringify(res));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    setToken(null);
    localStorage.removeItem('axon_user');
    localStorage.removeItem('axon_token');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: user?.role || null,
        isAuthenticated: !!user && !!token,
        isLoading,
        loginStudent,
        loginStaff,
        loginHOD,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
