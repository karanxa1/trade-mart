// Messages Page
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { messagesAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './Messages.css';

const Messages = () => {
  const { user } = useAuth();
  const toast = useToast();
  const [searchParams] = useSearchParams();
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  // Check for pre-selected user (from Product Detail "Chat with Seller")
  const targetUserId = searchParams.get('user');
  const productId = searchParams.get('product');

  useEffect(() => {
    if (user) {
      fetchConversations();
    }
  }, [user]);

  useEffect(() => {
    if (targetUserId && conversations.length > 0) {
      // Find existing conversation or create a temporary one state
      const existing = conversations.find(c => c.partner_id === targetUserId);
      if (existing) {
        selectConversation(existing);
      } else {
        // If no conversation exists, we prepare to start one
        // Ideally fetch partner details, but for now we might need a "New Chat" state
        // For simplicity, let's assume we just wait for user to send first message
        setActiveConversation({
          partner_id: targetUserId,
          partner_name: 'Seller', // Should fetch user name
          partner_avatar: null,
          is_new: true,
          product_id: productId
        });
      }
    }
  }, [targetUserId, conversations]);

  const fetchConversations = async () => {
    try {
      const response = await messagesAPI.getConversations(user.id);
      // Backend returns array directly, not wrapped in 'conversations'
      // Also uses 'partner_username' not 'partner_name'
      const convs = (response.data || []).map(c => ({
        ...c,
        partner_name: c.partner_username
      }));
      setConversations(convs);
    } catch (err) {
      console.error('Error fetching conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = async (conv) => {
    setActiveConversation(conv);
    if (!conv.is_new) {
      try {
        const response = await messagesAPI.getConversation(user.id, conv.partner_id);
        // Backend returns messages array directly in response.data.messages
        // Message fields: sender_id, receiver_id, content, created_at (not 'timestamp')
        const msgs = (response.data.messages || []).map(m => ({
          ...m,
          timestamp: m.created_at
        }));
        setMessages(msgs);
      } catch (err) {
        console.error('Error fetching messages:', err);
      }
    } else {
      setMessages([]);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeConversation) return;

    setSending(true);
    try {
      await messagesAPI.sendMessage(
        user.id,
        activeConversation.partner_id,
        newMessage,
        activeConversation.product_id || null
      );
      
      setNewMessage('');
      
      // Refresh messages
      const response = await messagesAPI.getConversation(user.id, activeConversation.partner_id);
      const msgs = (response.data.messages || []).map(m => ({
        ...m,
        timestamp: m.created_at
      }));
      setMessages(msgs);
      
      // Refresh conversation list to show latest message
      fetchConversations();
      
      if (activeConversation.is_new) {
        setActiveConversation(prev => ({ ...prev, is_new: false }));
      }

    } catch (err) {
      console.error('Error sending message:', err);
      toast.error('Failed to send message');
    } finally {
      setSending(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) return <div className="loading">Loading messages...</div>;

  return (
    <div className="messages-page">
      <div className="container">
        <h1>Messages</h1>
        
        <div className="messages-layout">
          <div className="conversations-list">
            {conversations.length === 0 && !targetUserId ? (
              <div className="no-conversations">No messages yet</div>
            ) : (
              conversations.map(conv => (
                <div 
                  key={conv.partner_id} 
                  className={`conversation-item ${activeConversation?.partner_id === conv.partner_id ? 'active' : ''}`}
                  onClick={() => selectConversation(conv)}
                >
                  <div className="conv-avatar">
                   <i className="fas fa-user"></i>
                  </div>
                  <div className="conv-info">
                    <h4>{conv.partner_name}</h4>
                    <p>{conv.last_message?.substring(0, 30)}...</p>
                  </div>
                  {conv.unread_count > 0 && <span className="unread-badge">{conv.unread_count}</span>}
                </div>
              ))
            )}
            
            {/* Show temporary item if starting new chat */}
            {activeConversation?.is_new && (
              <div className="conversation-item active">
                <div className="conv-avatar"><i className="fas fa-user"></i></div>
                <div className="conv-info">
                  <h4>New Chat</h4>
                  <p>Start a conversation...</p>
                </div>
              </div>
            )}
          </div>

          <div className="chat-window">
            {activeConversation ? (
              <>
                <div className="chat-header">
                  <div className="chat-partner-info">
                    <i className="fas fa-user-circle"></i>
                    <h3>{activeConversation.partner_name || 'User'}</h3>
                  </div>
                </div>

                <div className="chat-messages">
                  {messages.map((msg, index) => (
                    <div 
                      key={index} 
                      className={`message-bubble ${msg.sender_id === user.id ? 'sent' : 'received'}`}
                    >
                      <div className="message-content">
                        {msg.content}
                      </div>
                      <div className="message-time">
                        {formatTime(msg.timestamp)}
                      </div>
                    </div>
                  ))}
                  {messages.length === 0 && (
                    <div className="empty-chat">
                      <p>No messages yet. Say hello!</p>
                    </div>
                  )}
                </div>

                <div className="chat-input-area">
                  <form onSubmit={handleSendMessage}>
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type a message..."
                      disabled={sending}
                    />
                    <button type="submit" disabled={sending || !newMessage.trim()}>
                      <i className="fas fa-paper-plane"></i>
                    </button>
                  </form>
                </div>
              </>
            ) : (
              <div className="no-chat-selected">
                <i className="fas fa-comments"></i>
                <h3>Select a conversation</h3>
                <p>Choose a chat from the left to start messaging.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Messages;
