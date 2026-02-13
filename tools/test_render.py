# tests/test_render.py
import yaml
from jinja2 import Template
import glob

def test_rendering():
    # 1. 读取模板
    with open("./runtime/render.md", "r") as f:
        template_str = f.read()
        # 模拟 OpenClaw 的 fs.read，我们在 Python 里手动替换掉
        # 因为 Python Jinja 不直接支持 fs.read 函数
        template_str = template_str.replace("{% set soul = fs.read('./soul/active_soul.yaml') %}", "")

    # 2. 遍历所有种子进行测试
    seeds = glob.glob("./seeds/**/*.yaml", recursive=True)
    
    for seed_file in seeds:
        with open(seed_file, 'r') as f:
            soul_data = yaml.safe_load(f)
        
        try:
            # 尝试渲染
            t = Template(template_str)
            # 将种子数据注入变量 'soul'
            output = t.render(soul=soul_data)
            
            # 检查关键字段是否出现在结果中
            if soul_data['meta']['name'] not in output and "Nucleus" not in output:
                 print(f"⚠️ [WARN] {seed_file} rendered but seems empty.")
            else:
                 print(f"✅ [PASS] Render test for {seed_file}")
                 
        except Exception as e:
            print(f"❌ [FAIL] Rendering failed for {seed_file}: {e}")

if __name__ == "__main__":
    test_rendering()