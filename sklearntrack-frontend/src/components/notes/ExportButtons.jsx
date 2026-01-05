// FILE: ExportButtons.jsx - Complete Drive Integration
import React, { useState, useEffect } from 'react';
import { Download, Cloud, Mail, CheckCircle, AlertCircle, Link as LinkIcon } from 'lucide-react';
import api from '@/services/api';
import toast from 'react-hot-toast';

const ExportButtons = ({ note, onDriveStatusChange }) => {
  const [exporting, setExporting] = useState(false);
  const [uploadingToDrive, setUploadingToDrive] = useState(false);
  const [driveStatus, setDriveStatus] = useState({ connected: false, checking: true });

  useEffect(() => {
    checkDriveStatus();
  }, []);

  const checkDriveStatus = async () => {
    try {
      const response = await api.get('/api/notes/drive_status/');
      setDriveStatus({
        connected: response.data.connected,
        can_export: response.data.can_export,
        checking: false
      });
      if (onDriveStatusChange) {
        onDriveStatusChange(response.data);
      }
    } catch (error) {
      console.error('Error checking Drive status:', error);
      setDriveStatus({ connected: false, can_export: false, checking: false });
    }
  };

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      const response = await api.post(
        `/api/notes/${note.id}/export_pdf/`,
        {},
        { 
          responseType: 'blob',
          validateStatus: (status) => status < 500
        }
      );
      
      if (response.data.type === 'application/json') {
        const text = await response.data.text();
        const errorData = JSON.parse(text);
        toast.error(errorData.error || 'Failed to export PDF');
        return;
      }
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${note.title}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF exported successfully!');
    } catch (error) {
      console.error('Export error:', error);
      toast.error(error.response?.data?.error || 'Failed to export PDF');
    } finally {
      setExporting(false);
    }
  };

  const handleConnectDrive = async () => {
    try {
      const response = await api.get('/api/notes/google_auth_url/');
      if (response.data.auth_url) {
        const authWindow = window.open(
          response.data.auth_url,
          'Google Drive Auth',
          'width=600,height=700,left=100,top=100'
        );
        
        // Listen for auth success
        const handleMessage = (event) => {
          if (event.data.type === 'google-auth-success') {
            toast.success('Google Drive connected successfully!');
            checkDriveStatus();
            authWindow?.close();
          } else if (event.data.type === 'google-auth-error') {
            toast.error('Failed to connect Google Drive');
            authWindow?.close();
          }
        };
        
        window.addEventListener('message', handleMessage);
        
        // Cleanup listener when window closes
        const checkClosed = setInterval(() => {
          if (authWindow?.closed) {
            clearInterval(checkClosed);
            window.removeEventListener('message', handleMessage);
            checkDriveStatus();
          }
        }, 500);
      }
    } catch (error) {
      console.error('Auth error:', error);
      toast.error('Failed to initiate Google Drive connection');
    }
  };

  const handleExportToGoogleDrive = async () => {
    if (!driveStatus.connected) {
      handleConnectDrive();
      return;
    }

    setUploadingToDrive(true);
    try {
      const response = await api.post(`/api/notes/${note.id}/export_to_drive/`);
      
      if (response.data.success) {
        const message = response.data.updated 
          ? 'Note updated in Google Drive!' 
          : 'Note uploaded to Google Drive!';
        
        toast.success(
          <div>
            <p>{message}</p>
            {response.data.drive_link && (
              <a 
                href={response.data.drive_link} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 underline flex items-center gap-1 mt-1"
              >
                <LinkIcon size={14} />
                Open in Drive
              </a>
            )}
          </div>,
          { duration: 5000 }
        );
      } else if (response.data.needs_auth) {
        toast.error('Please reconnect Google Drive');
        handleConnectDrive();
      } else {
        toast.error(response.data.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Drive export error:', error);
      
      if (error.response?.status === 401 || error.response?.data?.needs_auth) {
        toast.error('Please reconnect Google Drive');
        handleConnectDrive();
      } else {
        toast.error(error.response?.data?.error || 'Failed to upload to Google Drive');
      }
    } finally {
      setUploadingToDrive(false);
    }
  };

  const handleSendDailyReport = async () => {
    try {
      const response = await api.post(`/api/notes/${note.id}/send_daily_report_email/`);
      
      if (response.data.success) {
        toast.success('Daily report sent to your email!');
      } else {
        toast.error('Failed to send report');
      }
    } catch (error) {
      console.error('Send report error:', error);
      toast.error('Failed to send report');
    }
  };

  return (
    <div className="flex gap-2 flex-wrap items-center">
      {/* Drive Connection Status */}
      {!driveStatus.checking && (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg text-sm">
          {driveStatus.connected ? (
            <>
              <CheckCircle size={16} className="text-green-600" />
              <span className="text-green-700 dark:text-green-400">Drive Connected</span>
            </>
          ) : (
            <>
              <AlertCircle size={16} className="text-orange-600" />
              <span className="text-orange-700 dark:text-orange-400">Drive Not Connected</span>
            </>
          )}
        </div>
      )}

      {/* Export PDF Button */}
      <button
        onClick={handleExportPDF}
        disabled={exporting}
        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
      >
        {exporting ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            Exporting...
          </>
        ) : (
          <>
            <Download size={16} />
            Export PDF
          </>
        )}
      </button>

      {/* Export to Google Drive Button */}
      <button
        onClick={handleExportToGoogleDrive}
        disabled={uploadingToDrive}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition disabled:opacity-50 ${
          driveStatus.connected
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-orange-600 text-white hover:bg-orange-700'
        }`}
      >
        {uploadingToDrive ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            Uploading...
          </>
        ) : (
          <>
            <Cloud size={16} />
            {driveStatus.connected ? 'Upload to Drive' : 'Connect Drive'}
          </>
        )}
      </button>

      {/* Send Daily Report Button */}

    </div>
  );
};

export default ExportButtons;