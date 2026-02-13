import yaml
import glob
import sys
import re
from jinja2 import Template, Environment, Undefined

# 定义一个宽松的 Undefined 类，防止模板因为无关变量报错
class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""

def mock_fs_read(path):
    """
    模拟 OpenClaw 的 fs.read 函数。
    但是在测试中，我们不真的去读文件，而是告诉测试逻辑：
    '灵魂数据已经通过变量传进来了，不需要再读了'
    """
    return {} # 返回空字典，因为我们在下面手动注入了 soul 变量

def test_rendering():
    # 1. 读取 System Prompt 模板
    try:
        with open("runtime/render.md", "r", encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print("❌ Critical: runtime/render.md not found!")
        sys.exit(1)

    # 2. 预处理模板
    # render.md 第一行通常是 {% set soul = fs.read(...) %}
    # 在 Python 测试中，我们手动注入 soul 变量，所以要把这一行注释掉或删掉，防止报错
    # 使用正则把整行替换成 Jinja2 注释
    template_content = re.sub(r'\{%\s*set\s+soul\s*=\s*fs\.read\([^)]*\)\s*%\}', '{# soul variable injected by test #}', template_content)

    # 3. 准备 Jinja2 环境
    env = Environment(undefined=SilentUndefined)
    
    # 4. 遍历所有种子进行渲染测试
    seeds = glob.glob("seeds/**/*.yaml", recursive=True)
    failed_count = 0

    print(f"🎨 Testing render simulation for {len(seeds)} seeds...")
    print("-" * 40)

    for seed_file in seeds:
        try:
            # 加载种子数据
            with open(seed_file, 'r', encoding='utf-8') as f:
                soul_data = yaml.safe_load(f)

            # 渲染！
            template = env.from_string(template_content)
            # 这里我们将 yaml 数据注入为 'soul' 变量，模拟 openclaw 的行为
            rendered_output = template.render(soul=soul_data, fs={'read': mock_fs_read})

            # 5. 检查输出是否包含关键信息 (冒烟测试)
            # 检查 Nucleus 是否被正确渲染
            if "LAYER 1: NUCLEUS" not in rendered_output:
                raise ValueError("Rendered output missing 'LAYER 1' header")
            
            # 检查 Persona 的任务是否被渲染
            mission = soul_data.get('persona', {}).get('current_mission')
            if mission and mission not in rendered_output:
                 raise ValueError(f"Mission '{mission}' not found in output")

            print(f"✅ {seed_file}: Rendered successfully ({len(rendered_output)} chars)")

        except Exception as e:
            print(f"❌ {seed_file}: Render FAILED")
            print(f"   Error: {str(e)}")
            failed_count += 1

    print("-" * 40)
    if failed_count > 0:
        print(f"🚨 Render test failed! {failed_count} seeds are broken.")
        sys.exit(1)
    else:
        print("✨ All seeds render perfectly!")
        sys.exit(0)

if __name__ == "__main__":
    test_rendering()