"""
Database Administration component for N2S TMMi Tracker
Provides backup, restore, and database management functionality
"""
import streamlit as st
import os
import glob
from datetime import datetime
from typing import List, Dict
import logging

from src.models.database import TMMiDatabase


def render_database_admin():
    """Render the database administration page"""
    
    st.header("Database Administration")
    st.markdown("Manage database backups, monitor health, and view statistics.")
    
    db = TMMiDatabase()
    
    # Database health status
    render_database_health(db)
    
    # Database statistics
    render_database_stats(db)
    
    # Backup and restore functionality
    render_backup_restore(db)
    
    # Advanced operations
    render_advanced_operations(db)


def render_database_health(db: TMMiDatabase):
    """Display database health status"""
    
    st.subheader("Database Health")
    
    # Check database integrity
    is_healthy = db.verify_database_integrity()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if is_healthy:
            st.success("✅ Database is healthy")
        else:
            st.error("❌ Database has issues")
    
    with col2:
        if os.path.exists(db.db_path):
            st.info(f"📁 Database location: {db.db_path}")
        else:
            st.warning("⚠️ Database file not found")
    
    with col3:
        if os.path.exists(db.db_path):
            file_size = os.path.getsize(db.db_path)
            size_mb = round(file_size / (1024 * 1024), 2)
            st.metric("Database Size", f"{size_mb} MB")


def render_database_stats(db: TMMiDatabase):
    """Display database statistics"""
    
    st.subheader("Database Statistics")
    
    try:
        stats = db.get_database_stats()
        
        if 'error' in stats:
            st.error(f"Error getting statistics: {stats['error']}")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Assessments", stats.get('total_assessments', 0))
        
        with col2:
            st.metric("Total Answers", stats.get('total_answers', 0))
        
        with col3:
            st.metric("Organizations", stats.get('total_organizations', 0))
        
        with col4:
            st.metric("Database Size", f"{stats.get('db_size_mb', 0)} MB")
        
        # Last assessment info
        if stats.get('last_assessment'):
            st.info(f"Last assessment: {stats['last_assessment']}")
        
    except Exception as e:
        st.error(f"Failed to get database statistics: {str(e)}")


def render_backup_restore(db: TMMiDatabase):
    """Render backup and restore functionality"""
    
    st.subheader("Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Create Backup")
        
        if st.button("Create Manual Backup", type="primary"):
            try:
                backup_path = db.backup_database()
                st.success("✅ Backup created successfully!")
                st.info(f"📁 Backup location: {backup_path}")
                logging.info(f"Manual backup created: {backup_path}")
            except Exception as e:
                st.error(f"❌ Backup failed: {str(e)}")
                logging.error(f"Manual backup failed: {str(e)}")
        
        # Automatic backup configuration
        st.markdown("**Automatic Backups**")
        backup_dir = os.environ.get('TMMI_BACKUP_DIR', 'backups')
        st.text(f"Directory: {backup_dir}")
        
        if os.path.exists(backup_dir):
            backup_files = glob.glob(os.path.join(backup_dir, "*.db"))
            st.text(f"Current backups: {len(backup_files)}")
        else:
            st.text("Backup directory not found")
    
    with col2:
        st.markdown("#### Restore from Backup")
        
        # List available backups
        backup_dir = os.environ.get('TMMI_BACKUP_DIR', 'backups')
        backup_files = []
        
        if os.path.exists(backup_dir):
            backup_files = glob.glob(os.path.join(backup_dir, "*.db"))
            backup_files.sort(key=os.path.getmtime, reverse=True)
        
        if backup_files:
            backup_options = {
                f: f"{os.path.basename(f)} ({datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')})"
                for f in backup_files
            }
            
            selected_backup = st.selectbox(
                "Select backup to restore",
                options=list(backup_options.keys()),
                format_func=lambda x: backup_options[x]
            )
            
            st.warning("⚠️ Restoring will overwrite the current database!")
            
            if st.button("Restore Database", type="secondary"):
                if selected_backup:
                    try:
                        success = db.restore_database(selected_backup)
                        if success:
                            st.success("✅ Database restored successfully!")
                            st.info("🔄 Please refresh the page to see changes.")
                            logging.info(f"Database restored from: {selected_backup}")
                        else:
                            st.error("❌ Database restore failed!")
                    except Exception as e:
                        st.error(f"❌ Restore failed: {str(e)}")
                        logging.error(f"Database restore failed: {str(e)}")
        else:
            st.info("No backup files found.")


def render_advanced_operations(db: TMMiDatabase):
    """Render advanced database operations"""
    
    st.subheader("Advanced Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Database Maintenance")
        
        if st.button("Verify Database Integrity"):
            with st.spinner("Checking database integrity..."):
                is_healthy = db.verify_database_integrity()
                
                if is_healthy:
                    st.success("✅ Database integrity check passed")
                else:
                    st.error("❌ Database integrity issues detected")
        
        if st.button("Vacuum Database"):
            try:
                import sqlite3
                with sqlite3.connect(db.db_path) as conn:
                    conn.execute("VACUUM")
                st.success("✅ Database vacuum completed")
                logging.info("Database vacuum completed")
            except Exception as e:
                st.error(f"❌ Vacuum failed: {str(e)}")
                logging.error(f"Database vacuum failed: {str(e)}")
    
    with col2:
        st.markdown("#### Export Data")
        
        if st.button("Download Database File"):
            try:
                with open(db.db_path, 'rb') as f:
                    db_data = f.read()
                
                filename = f"tmmi_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                st.download_button(
                    label="Download SQLite Database",
                    data=db_data,
                    file_name=filename,
                    mime="application/x-sqlite3"
                )
            except Exception as e:
                st.error(f"❌ Download failed: {str(e)}")
        
        if st.button("Export as JSON"):
            try:
                # This would require implementing a full data export function
                st.info("JSON export feature coming soon...")
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")


def render_backup_history():
    """Display backup history"""
    
    st.subheader("Backup History")
    
    backup_dir = os.environ.get('TMMI_BACKUP_DIR', 'backups')
    
    if not os.path.exists(backup_dir):
        st.info("No backup directory found.")
        return
    
    backup_files = glob.glob(os.path.join(backup_dir, "*.db"))
    
    if not backup_files:
        st.info("No backup files found.")
        return
    
    # Create backup history table
    backup_data = []
    for backup_file in backup_files:
        file_stat = os.stat(backup_file)
        backup_data.append({
            'Filename': os.path.basename(backup_file),
            'Created': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'Size (MB)': round(file_stat.st_size / (1024 * 1024), 2),
            'Path': backup_file
        })
    
    # Sort by creation time (newest first)
    backup_data.sort(key=lambda x: x['Created'], reverse=True)
    
    # Display table
    import pandas as pd
    df = pd.DataFrame(backup_data)
    st.dataframe(df[['Filename', 'Created', 'Size (MB)']], use_container_width=True)
    
    # Cleanup old backups
    if len(backup_data) > 10:
        st.warning(f"You have {len(backup_data)} backup files. Consider cleaning up old backups.")
        
        if st.button("Clean up old backups (keep 10 most recent)"):
            try:
                # Keep only the 10 most recent backups
                files_to_delete = [item['Path'] for item in backup_data[10:]]
                
                for file_path in files_to_delete:
                    os.remove(file_path)
                
                st.success(f"✅ Cleaned up {len(files_to_delete)} old backup files")
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"❌ Cleanup failed: {str(e)}")


if __name__ == "__main__":
    render_database_admin()
