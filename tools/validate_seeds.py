# tests/validate_seeds.py
import yaml
import jsonschema
import glob
import sys

# 定义灵魂的合法结构
soul_schema = {
    "type": "object",
    "required": ["meta", "nucleus", "persona", "pulse"],
    "properties": {
        "nucleus": {
            "type": "object",
            "required": ["drives", "prime_directives"],
            "properties": {
                "drives": {"type": "object"} # 必须是字典
            }
        },
        # ... 其他字段定义
    }
}

def validate():
    files = glob.glob("./seeds/**/*.yaml", recursive=True)
    has_error = False
    
    for f in files:
        try:
            with open(f, 'r') as stream:
                data = yaml.safe_load(stream)
                jsonschema.validate(instance=data, schema=soul_schema)
                print(f"✅ [PASS] {f}")
        except Exception as e:
            print(f"❌ [FAIL] {f}: {str(e)}")
            has_error = True
            
    if has_error:
        sys.exit(1)

if __name__ == "__main__":
    validate()