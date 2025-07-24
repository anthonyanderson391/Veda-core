# Enhanced Memory Manager

A robust, production-ready memory management system for persistent learning and command tracking with advanced features like error handling, automatic cleanup, and backup recovery.

## Key Improvements

### 🛡️ **Reliability & Safety**
- **Atomic Operations**: Write-then-move pattern prevents data corruption
- **Automatic Backup**: Creates backups before each save operation
- **Error Recovery**: Automatic recovery from backup if main file is corrupted
- **Comprehensive Error Handling**: Graceful handling of all file operations

### ⏰ **Enhanced Data Tracking**
- **Timestamps**: All entries include ISO format timestamps
- **Metadata**: Tracks creation time, last update, and version info
- **Command Details**: Optional details field for command logs
- **Context**: Store context information with corrections
- **Confidence Scores**: Preferred phrases can include confidence levels

### 🧹 **Automatic Cleanup**
- **Log Retention**: Configurable retention period (default: 30 days)
- **Size Limits**: Maximum log entries limit (default: 1000)
- **Manual Cleanup**: Methods to manually clear old data

### 📊 **Analytics & Insights**
- **Command Statistics**: Success/failure counts per command
- **Recent Failures**: Get recent failures within specified timeframe
- **Legacy Compatibility**: Backward compatible with original API

### 🔧 **Developer Experience**
- **Type Hints**: Full type annotations for better IDE support
- **Logging**: Comprehensive logging for debugging
- **Export/Import**: Memory export functionality for backups
- **Class-based Design**: Object-oriented approach with legacy wrappers

## Usage

### Basic Usage (Legacy Compatible)
```python
from memory_manager import log_command, save_correction, get_preferred_phrase

# Log commands (same as before)
log_command("git pull", success=True)
log_command("npm install", success=False)

# Save corrections (same as before)
save_correction("npm install", "sudo npm install")

# Get preferred phrases (same as before)
greeting = get_preferred_phrase("greeting")
```

### Advanced Usage (New Features)
```python
from memory_manager import MemoryManager

# Create memory manager instance
memory = MemoryManager()

# Log commands with details and timestamps
memory.log_command("git pull", success=True, details="Updated 5 files")
memory.log_command("npm install", success=False, details="Permission denied")

# Save corrections with context
memory.save_correction(
    "npm install", 
    "sudo npm install", 
    context="Permission issues on Linux systems"
)

# Set preferred phrases with confidence scores
memory.set_preferred_phrase("greeting", "Hello there!", confidence=0.9)

# Get command statistics
stats = memory.get_command_stats("npm install")
print(f"Total: {stats['total']}, Success: {stats['success']}, Failures: {stats['failure']}")

# Get recent failures
failures = memory.get_recent_failures(days=7)
for failure in failures:
    print(f"Failed: {failure['command']} - {failure.get('details', 'No details')}")

# Export memory for backup
memory.export_memory("backup.json")

# Manual cleanup of old logs
memory.clear_old_logs(days=14)
```

## Configuration

You can customize the behavior by modifying these constants:

```python
MAX_COMMAND_LOGS = 1000      # Maximum number of command logs to keep
LOG_RETENTION_DAYS = 30      # Days to keep command logs
FAILURE_THRESHOLD = 3        # Number of failures before prompting for correction
```

## File Structure

The memory system creates these files:
- `veda_memory.json` - Main memory file
- `veda_memory_backup.json` - Automatic backup file
- `*.tmp` - Temporary files during atomic operations (auto-cleaned)

## Memory File Format

```json
{
    "corrections": {
        "original_text": {
            "correction": "corrected_text",
            "timestamp": "2024-01-01T12:00:00",
            "context": "Additional context"
        }
    },
    "preferred_phrases": {
        "category": {
            "phrase": "preferred phrase",
            "confidence": 0.9,
            "timestamp": "2024-01-01T12:00:00"
        }
    },
    "command_logs": [
        {
            "command": "git pull",
            "success": true,
            "timestamp": "2024-01-01T12:00:00",
            "details": "Updated 5 files"
        }
    ],
    "metadata": {
        "created_at": "2024-01-01T12:00:00",
        "last_updated": "2024-01-01T12:00:00",
        "version": "1.0"
    }
}
```

## Error Handling

The system handles various error scenarios:
- **File corruption**: Automatic recovery from backup
- **Missing files**: Automatic reinitialization
- **Permission issues**: Graceful error logging
- **JSON parsing errors**: Backup recovery and reinitialization
- **Disk space issues**: Atomic operations prevent partial writes

## Logging

The system uses Python's logging module. Configure logging level:

```python
import logging
logging.getLogger('memory_manager').setLevel(logging.DEBUG)
```

## Migration from Legacy

The enhanced system is fully backward compatible. Existing code will work without changes, but you can gradually adopt new features:

1. **Immediate**: All existing functions work with enhanced error handling
2. **Gradual**: Start using `MemoryManager()` class for new features
3. **Full**: Eventually migrate to class-based approach for all functionality

## Testing

Run the example to test functionality:

```bash
python example_usage.py
```

This will demonstrate all features and create sample data files.
