import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to memory file
MEMORY_FILE = "veda_memory.json"
BACKUP_FILE = "veda_memory_backup.json"

# Configuration constants
MAX_COMMAND_LOGS = 1000  # Maximum number of command logs to keep
LOG_RETENTION_DAYS = 30  # Days to keep command logs
FAILURE_THRESHOLD = 3    # Number of failures before prompting for correction

class MemoryManager:
    """Enhanced memory management system with error handling and cleanup."""
    
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self.backup_file = memory_file.replace('.json', '_backup.json')
        self.init_memory()
    
    def init_memory(self) -> bool:
        """Initialize memory file with default structure."""
        try:
            if not os.path.exists(self.memory_file):
                default_memory = {
                    "corrections": {},
                    "preferred_phrases": {},
                    "command_logs": [],
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }
                return self._save_memory_atomic(default_memory)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize memory: {e}")
            return False
    
    def load_memory(self) -> Optional[Dict[str, Any]]:
        """Load memory with error handling and backup recovery."""
        try:
            with open(self.memory_file, "r", encoding='utf-8') as f:
                memory = json.load(f)
                # Ensure all required keys exist
                if not all(key in memory for key in ["corrections", "preferred_phrases", "command_logs"]):
                    logger.warning("Memory file missing required keys, reinitializing...")
                    self.init_memory()
                    return self.load_memory()
                return memory
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load memory: {e}")
            # Try to load from backup
            if self._load_from_backup():
                return self.load_memory()
            # If backup fails, reinitialize
            logger.info("Reinitializing memory file...")
            self.init_memory()
            return self.load_memory()
        except Exception as e:
            logger.error(f"Unexpected error loading memory: {e}")
            return None
    
    def _save_memory_atomic(self, memory: Dict[str, Any]) -> bool:
        """Save memory using atomic operations to prevent corruption."""
        try:
            # Update metadata
            if "metadata" not in memory:
                memory["metadata"] = {}
            memory["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Create backup before saving
            if os.path.exists(self.memory_file):
                shutil.copy2(self.memory_file, self.backup_file)
            
            # Write to temporary file first
            with tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                           dir=os.path.dirname(self.memory_file) or '.', 
                                           suffix='.tmp') as temp_file:
                json.dump(memory, temp_file, indent=4, ensure_ascii=False)
                temp_file_path = temp_file.name
            
            # Atomic move
            shutil.move(temp_file_path, self.memory_file)
            return True
            
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            # Clean up temp file if it exists
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return False
    
    def _load_from_backup(self) -> bool:
        """Load memory from backup file."""
        try:
            if os.path.exists(self.backup_file):
                shutil.copy2(self.backup_file, self.memory_file)
                logger.info("Restored memory from backup")
                return True
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
        return False
    
    def log_command(self, command: str, success: bool = True, details: Optional[str] = None) -> bool:
        """Log command usage with timestamp and optional details."""
        try:
            memory = self.load_memory()
            if memory is None:
                return False
            
            log_entry = {
                "command": command,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "details": details
            }
            
            memory["command_logs"].append(log_entry)
            
            # Clean up old logs if necessary
            self._cleanup_command_logs(memory)
            
            return self._save_memory_atomic(memory)
        except Exception as e:
            logger.error(f"Failed to log command: {e}")
            return False
    
    def _cleanup_command_logs(self, memory: Dict[str, Any]) -> None:
        """Clean up old command logs based on retention policy."""
        try:
            logs = memory["command_logs"]
            
            # Remove logs older than retention period
            cutoff_date = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
            logs = [log for log in logs if datetime.fromisoformat(log.get("timestamp", "1970-01-01")) > cutoff_date]
            
            # Keep only the most recent logs if still too many
            if len(logs) > MAX_COMMAND_LOGS:
                logs = logs[-MAX_COMMAND_LOGS:]
            
            memory["command_logs"] = logs
        except Exception as e:
            logger.error(f"Failed to cleanup command logs: {e}")
    
    def save_correction(self, original: str, correction: str, context: Optional[str] = None) -> bool:
        """Store correction with optional context."""
        try:
            memory = self.load_memory()
            if memory is None:
                return False
            
            correction_entry = {
                "correction": correction,
                "timestamp": datetime.now().isoformat(),
                "context": context
            }
            
            memory["corrections"][original] = correction_entry
            return self._save_memory_atomic(memory)
        except Exception as e:
            logger.error(f"Failed to save correction: {e}")
            return False
    
    def get_correction(self, original: str) -> Optional[str]:
        """Get correction for a given original text."""
        try:
            memory = self.load_memory()
            if memory is None:
                return None
            
            correction_entry = memory["corrections"].get(original)
            if isinstance(correction_entry, dict):
                return correction_entry.get("correction")
            elif isinstance(correction_entry, str):
                # Handle legacy format
                return correction_entry
            return None
        except Exception as e:
            logger.error(f"Failed to get correction: {e}")
            return None
    
    def set_preferred_phrase(self, category: str, new_phrase: str, confidence: float = 1.0) -> bool:
        """Set preferred phrase with confidence score."""
        try:
            memory = self.load_memory()
            if memory is None:
                return False
            
            phrase_entry = {
                "phrase": new_phrase,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
            
            memory["preferred_phrases"][category] = phrase_entry
            return self._save_memory_atomic(memory)
        except Exception as e:
            logger.error(f"Failed to set preferred phrase: {e}")
            return False
    
    def get_preferred_phrase(self, category: str) -> Optional[str]:
        """Retrieve preferred phrase for a category."""
        try:
            memory = self.load_memory()
            if memory is None:
                return None
            
            phrase_entry = memory["preferred_phrases"].get(category)
            if isinstance(phrase_entry, dict):
                return phrase_entry.get("phrase")
            elif isinstance(phrase_entry, str):
                # Handle legacy format
                return phrase_entry
            return None
        except Exception as e:
            logger.error(f"Failed to get preferred phrase: {e}")
            return None
    
    def should_prompt_for_correction(self, command: str, threshold: int = FAILURE_THRESHOLD) -> bool:
        """Check if correction should be prompted based on failure count."""
        try:
            memory = self.load_memory()
            if memory is None:
                return False
            
            failures = [log for log in memory["command_logs"] 
                        if log["command"] == command and not log["success"]]
            return len(failures) >= threshold
        except Exception as e:
            logger.error(f"Failed to check correction prompt: {e}")
            return False
    
    def get_command_stats(self, command: str) -> Dict[str, int]:
        """Get statistics for a specific command."""
        try:
            memory = self.load_memory()
            if memory is None:
                return {"total": 0, "success": 0, "failure": 0}
            
            command_logs = [log for log in memory["command_logs"] if log["command"] == command]
            total = len(command_logs)
            success = len([log for log in command_logs if log["success"]])
            failure = total - success
            
            return {"total": total, "success": success, "failure": failure}
        except Exception as e:
            logger.error(f"Failed to get command stats: {e}")
            return {"total": 0, "success": 0, "failure": 0}
    
    def get_recent_failures(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent command failures within specified days."""
        try:
            memory = self.load_memory()
            if memory is None:
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_failures = [
                log for log in memory["command_logs"]
                if not log["success"] and 
                datetime.fromisoformat(log.get("timestamp", "1970-01-01")) > cutoff_date
            ]
            
            return recent_failures
        except Exception as e:
            logger.error(f"Failed to get recent failures: {e}")
            return []
    
    def export_memory(self, export_path: str) -> bool:
        """Export memory to a specified file."""
        try:
            memory = self.load_memory()
            if memory is None:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to export memory: {e}")
            return False
    
    def clear_old_logs(self, days: int = LOG_RETENTION_DAYS) -> bool:
        """Manually clear logs older than specified days."""
        try:
            memory = self.load_memory()
            if memory is None:
                return False
            
            cutoff_date = datetime.now() - timedelta(days=days)
            original_count = len(memory["command_logs"])
            
            memory["command_logs"] = [
                log for log in memory["command_logs"]
                if datetime.fromisoformat(log.get("timestamp", "1970-01-01")) > cutoff_date
            ]
            
            cleaned_count = original_count - len(memory["command_logs"])
            if cleaned_count > 0:
                logger.info(f"Cleaned {cleaned_count} old log entries")
                return self._save_memory_atomic(memory)
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear old logs: {e}")
            return False


# Legacy function wrappers for backward compatibility
_memory_manager = MemoryManager()

def init_memory():
    """Legacy wrapper for init_memory."""
    return _memory_manager.init_memory()

def load_memory():
    """Legacy wrapper for load_memory."""
    return _memory_manager.load_memory()

def save_memory(memory):
    """Legacy wrapper for save_memory."""
    return _memory_manager._save_memory_atomic(memory)

def log_command(command, success=True):
    """Legacy wrapper for log_command."""
    return _memory_manager.log_command(command, success)

def save_correction(original, correction):
    """Legacy wrapper for save_correction."""
    return _memory_manager.save_correction(original, correction)

def set_preferred_phrase(category, new_phrase):
    """Legacy wrapper for set_preferred_phrase."""
    return _memory_manager.set_preferred_phrase(category, new_phrase)

def get_preferred_phrase(category):
    """Legacy wrapper for get_preferred_phrase."""
    return _memory_manager.get_preferred_phrase(category)

def should_prompt_for_correction(command):
    """Legacy wrapper for should_prompt_for_correction."""
    return _memory_manager.should_prompt_for_correction(command)