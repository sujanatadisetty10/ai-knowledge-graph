"""
Configuration profiles for different use cases and LLM providers.
"""
import os
from typing import Dict, Any, List
import toml


class ConfigurationProfiles:
    """Manages different configuration profiles for various scenarios."""
    
    @staticmethod
    def get_openai_profile() -> Dict[str, Any]:
        """Configuration profile for OpenAI API."""
        return {
            "llm": {
                "model": "gpt-4o",
                "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
                "base_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 4096,
                "temperature": 0.2
            },
            "chunking": {
                "chunk_size": 200,
                "overlap": 30
            },
            "standardization": {
                "enabled": True,
                "use_llm_for_entities": True
            },
            "inference": {
                "enabled": True,
                "use_llm_for_inference": True,
                "apply_transitive": True
            },
            "visualization": {
                "edge_smooth": "continuous"
            },
            "neo4j": {
                "enabled": False,
                "uri": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "password",
                "graph_name": "OpenAI_KnowledgeGraph",
                "clear_existing": False
            }
        }
    
    @staticmethod
    def get_claude_profile() -> Dict[str, Any]:
        """Configuration profile for Anthropic Claude."""
        return {
            "llm": {
                "model": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key"),
                "base_url": "https://api.anthropic.com/v1/messages",
                "max_tokens": 4096,
                "temperature": 0.3
            },
            "chunking": {
                "chunk_size": 250,
                "overlap": 40
            },
            "standardization": {
                "enabled": True,
                "use_llm_for_entities": True
            },
            "inference": {
                "enabled": True,
                "use_llm_for_inference": True,
                "apply_transitive": True
            },
            "visualization": {
                "edge_smooth": "dynamic"
            }
        }
    
    @staticmethod
    def get_ollama_profile(model: str = "llama3.2") -> Dict[str, Any]:
        """Configuration profile for Ollama local models."""
        return {
            "llm": {
                "model": model,
                "api_key": "ollama-local",
                "base_url": "http://localhost:11434/v1/chat/completions",
                "max_tokens": 8192,
                "temperature": 0.4
            },
            "chunking": {
                "chunk_size": 150,
                "overlap": 25
            },
            "standardization": {
                "enabled": True,
                "use_llm_for_entities": True
            },
            "inference": {
                "enabled": True,
                "use_llm_for_inference": True,
                "apply_transitive": True
            },
            "visualization": {
                "edge_smooth": False
            },
            "neo4j": {
                "enabled": False,
                "uri": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "password",
                "graph_name": f"Ollama_{model.replace('.', '_')}_KG",
                "clear_existing": False
            }
        }
    
    @staticmethod
    def get_fast_processing_profile() -> Dict[str, Any]:
        """Configuration profile optimized for speed."""
        return {
            "llm": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
                "base_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 2048,
                "temperature": 0.1
            },
            "chunking": {
                "chunk_size": 100,
                "overlap": 15
            },
            "standardization": {
                "enabled": True,
                "use_llm_for_entities": False  # Disable LLM for speed
            },
            "inference": {
                "enabled": True,
                "use_llm_for_inference": False,  # Disable LLM for speed
                "apply_transitive": True
            },
            "visualization": {
                "edge_smooth": False
            }
        }
    
    @staticmethod
    def get_high_quality_profile() -> Dict[str, Any]:
        """Configuration profile optimized for quality."""
        return {
            "llm": {
                "model": "gpt-4o",
                "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
                "base_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 8192,
                "temperature": 0.1
            },
            "chunking": {
                "chunk_size": 300,
                "overlap": 50
            },
            "standardization": {
                "enabled": True,
                "use_llm_for_entities": True
            },
            "inference": {
                "enabled": True,
                "use_llm_for_inference": True,
                "apply_transitive": True
            },
            "visualization": {
                "edge_smooth": "continuous"
            }
        }
    
    @staticmethod
    def get_minimal_profile() -> Dict[str, Any]:
        """Configuration profile with minimal processing."""
        return {
            "llm": {
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
                "base_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 1024,
                "temperature": 0.2
            },
            "chunking": {
                "chunk_size": 80,
                "overlap": 10
            },
            "standardization": {
                "enabled": False  # Disable standardization
            },
            "inference": {
                "enabled": False  # Disable inference
            },
            "visualization": {
                "edge_smooth": False
            }
        }
    
    @staticmethod
    def get_research_profile() -> Dict[str, Any]:
        """Configuration profile for academic research."""
        return {
            "llm": {
                "model": "gpt-4o",
                "api_key": os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
                "base_url": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 8192,
                "temperature": 0.0  # Very deterministic
            },
            "chunking": {
                "chunk_size": 250,
                "overlap": 40
            },
            "standardization": {
                "enabled": True,
                "use_llm_for_entities": True
            },
            "inference": {
                "enabled": True,
                "use_llm_for_inference": True,
                "apply_transitive": True
            },
            "visualization": {
                "edge_smooth": "continuous"
            },
            "neo4j": {
                "enabled": True,
                "uri": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "password",
                "graph_name": "Research_KnowledgeGraph",
                "clear_existing": False
            }
        }
    
    @staticmethod
    def get_available_profiles() -> List[str]:
        """Get list of available configuration profiles."""
        return [
            "openai",
            "claude", 
            "ollama",
            "fast_processing",
            "high_quality",
            "minimal",
            "research"
        ]
    
    @staticmethod
    def create_profile_config(profile_name: str, output_path: str, **kwargs) -> bool:
        """
        Create a configuration file from a profile.
        
        Args:
            profile_name: Name of the profile to use
            output_path: Path where to save the configuration file
            **kwargs: Additional configuration overrides
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the profile configuration
            if profile_name == "openai":
                config = ConfigurationProfiles.get_openai_profile()
            elif profile_name == "claude":
                config = ConfigurationProfiles.get_claude_profile()
            elif profile_name == "ollama":
                model = kwargs.get("model", "llama3.2")
                config = ConfigurationProfiles.get_ollama_profile(model)
            elif profile_name == "fast_processing":
                config = ConfigurationProfiles.get_fast_processing_profile()
            elif profile_name == "high_quality":
                config = ConfigurationProfiles.get_high_quality_profile()
            elif profile_name == "minimal":
                config = ConfigurationProfiles.get_minimal_profile()
            elif profile_name == "research":
                config = ConfigurationProfiles.get_research_profile()
            else:
                raise ValueError(f"Unknown profile: {profile_name}")
            
            # Apply any overrides
            for key, value in kwargs.items():
                if key in config:
                    if isinstance(config[key], dict) and isinstance(value, dict):
                        config[key].update(value)
                    else:
                        config[key] = value
            
            # Save configuration file
            with open(output_path, 'w') as f:
                toml.dump(config, f)
            
            print(f"Created {profile_name} configuration profile: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error creating profile configuration: {e}")
            return False


def create_all_profiles(output_dir: str = "configs") -> None:
    """
    Create configuration files for all available profiles.
    
    Args:
        output_dir: Directory to save configuration files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    profiles = ConfigurationProfiles.get_available_profiles()
    
    for profile in profiles:
        output_path = os.path.join(output_dir, f"config_{profile}.toml")
        ConfigurationProfiles.create_profile_config(profile, output_path)
    
    # Create some Ollama variants
    ollama_models = ["llama3.2", "gemma2", "mistral", "codellama"]
    for model in ollama_models:
        output_path = os.path.join(output_dir, f"config_ollama_{model.replace('.', '_')}.toml")
        ConfigurationProfiles.create_profile_config("ollama", output_path, model=model)
    
    print(f"Created {len(profiles) + len(ollama_models)} configuration profiles in {output_dir}/")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python config_profiles.py <profile_name> [output_path]")
        print(f"Available profiles: {', '.join(ConfigurationProfiles.get_available_profiles())}")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else f"config_{profile_name}.toml"
    
    if profile_name == "all":
        create_all_profiles()
    else:
        ConfigurationProfiles.create_profile_config(profile_name, output_path)
