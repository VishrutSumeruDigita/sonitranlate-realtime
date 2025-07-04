#!/usr/bin/env python3
"""
Channel Manager for SoniTranslate Live Stream API

This module manages YouTube channel configurations and provides
easy access to predefined channels.
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ChannelInfo:
    name: str
    url: str
    description: str
    languages: List[str]

class ChannelManager:
    """Manages YouTube channel configurations."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.channels = {}
        self.default_settings = {}
        self.load_config()
    
    def load_config(self):
        """Load channel configuration from JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.channels = {}
                for category, channel_list in config.get('channels', {}).items():
                    self.channels[category] = [
                        ChannelInfo(
                            name=ch['name'],
                            url=ch['url'], 
                            description=ch['description'],
                            languages=ch['languages']
                        ) for ch in channel_list
                    ]
                
                self.default_settings = config.get('default_settings', {})
                
            except Exception as e:
                print(f"Error loading config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration if none exists."""
        self.channels = {
            "news": [
                ChannelInfo(
                    name="BBC News",
                    url="https://www.youtube.com/@BBCNews",
                    description="British Broadcasting Corporation",
                    languages=["english", "tamil", "hindi"]
                )
            ]
        }
        self.default_settings = {
            "chunk_duration": 30,
            "transcriber_model": "base",
            "origin_language": "Automatic detection"
        }
    
    def get_all_channels(self) -> Dict[str, List[ChannelInfo]]:
        """Get all channels organized by category."""
        return self.channels
    
    def get_channels_by_category(self, category: str) -> List[ChannelInfo]:
        """Get channels in a specific category."""
        return self.channels.get(category, [])
    
    def get_channel_by_name(self, name: str) -> Optional[ChannelInfo]:
        """Find a channel by name across all categories."""
        for category_channels in self.channels.values():
            for channel in category_channels:
                if channel.name.lower() == name.lower():
                    return channel
        return None
    
    def get_channels_for_language(self, language: str) -> List[ChannelInfo]:
        """Get all channels that support a specific language."""
        matching_channels = []
        for category_channels in self.channels.values():
            for channel in category_channels:
                if language in channel.languages:
                    matching_channels.append(channel)
        return matching_channels
    
    def add_channel(self, category: str, name: str, url: str, 
                   description: str = "", languages: List[str] = None):
        """Add a new channel to the configuration."""
        if languages is None:
            languages = ["english"]
        
        new_channel = ChannelInfo(name, url, description, languages)
        
        if category not in self.channels:
            self.channels[category] = []
        
        self.channels[category].append(new_channel)
        self.save_config()
    
    def remove_channel(self, name: str) -> bool:
        """Remove a channel by name."""
        for category, channel_list in self.channels.items():
            for i, channel in enumerate(channel_list):
                if channel.name.lower() == name.lower():
                    del channel_list[i]
                    self.save_config()
                    return True
        return False
    
    def save_config(self):
        """Save current configuration to file."""
        config = {
            "channels": {},
            "default_settings": self.default_settings
        }
        
        for category, channel_list in self.channels.items():
            config["channels"][category] = [
                {
                    "name": ch.name,
                    "url": ch.url,
                    "description": ch.description,
                    "languages": ch.languages
                } for ch in channel_list
            ]
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def list_channels_formatted(self) -> str:
        """Get a formatted string listing all channels."""
        output = []
        for category, channel_list in self.channels.items():
            output.append(f"\n📂 {category.upper()}")
            output.append("=" * (len(category) + 4))
            
            for channel in channel_list:
                output.append(f"📺 {channel.name}")
                output.append(f"   URL: {channel.url}")
                output.append(f"   Description: {channel.description}")
                output.append(f"   Languages: {', '.join(channel.languages)}")
                output.append("")
        
        return "\n".join(output)


def main():
    """Example usage of ChannelManager."""
    
    manager = ChannelManager()
    
    print("📺 Available YouTube Channels")
    print("=" * 40)
    print(manager.list_channels_formatted())
    
    # Example: Get channels for Tamil
    tamil_channels = manager.get_channels_for_language("tamil")
    print(f"\n🎯 Channels supporting Tamil translation ({len(tamil_channels)}):")
    for channel in tamil_channels:
        print(f"  - {channel.name}: {channel.url}")
    
    # Example: Find a specific channel
    nasa_channel = manager.get_channel_by_name("NASA")
    if nasa_channel:
        print(f"\n🚀 NASA Channel found: {nasa_channel.url}")

if __name__ == "__main__":
    main() 