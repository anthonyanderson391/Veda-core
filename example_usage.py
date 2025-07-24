#!/usr/bin/env python3
"""
Example usage of the enhanced MemoryManager class.
This demonstrates the new features and improvements.
"""

from memory_manager import MemoryManager
import time

def main():
    # Create memory manager instance
    memory = MemoryManager()
    
    print("=== Enhanced Memory Manager Demo ===\n")
    
    # 1. Log some commands with details
    print("1. Logging commands...")
    memory.log_command("git pull", success=True, details="Updated 5 files")
    memory.log_command("npm install", success=False, details="Network timeout")
    memory.log_command("npm install", success=False, details="Permission denied")
    memory.log_command("npm install", success=True, details="Installed with sudo")
    memory.log_command("python test.py", success=True)
    
    # 2. Save corrections with context
    print("2. Saving corrections...")
    memory.save_correction(
        "npm install", 
        "sudo npm install", 
        context="Permission issues on Linux systems"
    )
    memory.save_correction(
        "git push origin master", 
        "git push origin main", 
        context="Default branch changed to main"
    )
    
    # 3. Set preferred phrases with confidence
    print("3. Setting preferred phrases...")
    memory.set_preferred_phrase("greeting", "Hello there!", confidence=0.9)
    memory.set_preferred_phrase("error_response", "I apologize for the confusion", confidence=0.8)
    
    # 4. Check if correction should be prompted
    print("4. Checking correction prompts...")
    should_prompt = memory.should_prompt_for_correction("npm install")
    print(f"Should prompt for 'npm install' correction: {should_prompt}")
    
    # 5. Get command statistics
    print("5. Command statistics...")
    stats = memory.get_command_stats("npm install")
    print(f"npm install stats: {stats}")
    
    # 6. Get recent failures
    print("6. Recent failures...")
    failures = memory.get_recent_failures(days=1)
    print(f"Recent failures: {len(failures)} found")
    for failure in failures:
        print(f"  - {failure['command']}: {failure.get('details', 'No details')}")
    
    # 7. Get corrections and preferred phrases
    print("7. Retrieving stored data...")
    correction = memory.get_correction("npm install")
    print(f"Correction for 'npm install': {correction}")
    
    greeting = memory.get_preferred_phrase("greeting")
    print(f"Preferred greeting: {greeting}")
    
    # 8. Export memory for backup
    print("8. Exporting memory...")
    export_success = memory.export_memory("memory_backup.json")
    print(f"Memory export successful: {export_success}")
    
    # 9. Demonstrate legacy function compatibility
    print("9. Testing legacy functions...")
    from memory_manager import log_command, get_preferred_phrase
    log_command("legacy_test", success=True)
    legacy_greeting = get_preferred_phrase("greeting")
    print(f"Legacy function result: {legacy_greeting}")
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()