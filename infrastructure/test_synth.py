#!/usr/bin/env python3
"""
Simple test to verify CDK app can be synthesized without errors
"""
import subprocess
import sys


def test_cdk_synth():
    """Test that CDK synth runs without errors"""
    try:
        result = subprocess.run(
            ["cdk", "synth", "--context", "env=dev"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print("❌ CDK synth failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        print("✅ CDK synth successful!")
        print(f"Generated {result.stdout.count('Resources:')} stack(s)")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ CDK synth timed out")
        return False
    except FileNotFoundError:
        print("❌ CDK CLI not found. Install with: npm install -g aws-cdk")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_cdk_synth()
    sys.exit(0 if success else 1)
