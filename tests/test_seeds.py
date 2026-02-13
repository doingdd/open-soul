import yaml
import glob
import sys
import os

# === 定义 SSOP 标准 Schema ===
# 这是灵魂必须遵守的法律
SOUL_SCHEMA = {
    "required_roots": ["meta", "nucleus", "persona", "pulse"],
    "nucleus": ["drives", "prime_directives"],
    "persona": ["current_mission", "unlocked_skills", "memory_summary"],
    "pulse": ["tone", "formatting_preference"]
}

def validate_structure(data, filename):
    errors = []
    
    # 1. 检查根节点
    for root in SOUL_SCHEMA["required_roots"]:
        if root not in data:
            errors.append(f"Missing root section: '{root}'")
            
    # 2. 检查 Nucleus (内核层)
    if "nucleus" in data:
        for field in SOUL_SCHEMA["nucleus"]:
            if field not in data["nucleus"]:
                errors.append(f"Missing field in nucleus: '{field}'")
        # 检查 drives 是否为字典且数值在 0-1 之间
        if "drives" in data["nucleus"] and isinstance(data["nucleus"]["drives"], dict):
            for drive, value in data["nucleus"]["drives"].items():
                if not (0 <= float(value) <= 1):
                    errors.append(f"Drive '{drive}' value {value} is out of range (0.0 - 1.0)")

    # 3. 检查 Persona (交互层)
    if "persona" in data:
        for field in SOUL_SCHEMA["persona"]:
            if field not in data["persona"]:
                errors.append(f"Missing field in persona: '{field}'")

    return errors

def main():
    # 查找所有 .yaml 文件
    seed_files = glob.glob("seeds/**/*.yaml", recursive=True)
    if not seed_files:
        print("⚠️  No seeds found in seeds/")
        return

    failed_count = 0

    print(f"🔍 Found {len(seed_files)} seeds. Validating...")
    print("-" * 40)

    for f in seed_files:
        try:
            with open(f, 'r', encoding='utf-8') as stream:
                data = yaml.safe_load(stream)
                
            if not data:
                print(f"❌ {f}: File is empty")
                failed_count += 1
                continue

            errors = validate_structure(data, f)
            
            if errors:
                print(f"❌ {f}: FAILED")
                for e in errors:
                    print(f"   - {e}")
                failed_count += 1
            else:
                print(f"✅ {f}: PASSED")

        except yaml.YAMLError as exc:
            print(f"❌ {f}: Invalid YAML syntax - {exc}")
            failed_count += 1

    print("-" * 40)
    if failed_count > 0:
        print(f"🚨 Validation failed! {failed_count} seeds have errors.")
        sys.exit(1)
    else:
        print("✨ All seeds look good!")
        sys.exit(0)

if __name__ == "__main__":
    main()