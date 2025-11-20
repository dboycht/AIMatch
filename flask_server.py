"""
AI学习笔记生成器 - Flask后端主程序
Stu ID: 032530213@NUAA
email: chenghaotian@nuaa.edu.cn
version: 1.0
"""
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from data_manager import *

app = Flask(__name__)

# 配置常量
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def manager(text, upload_files, mode):
    """
    处理中心
    :param text: 输入文本
    :param upload_files: 上传的文件
    :param mode: 处理模式
    :return: 路径
    """
    try:
        # 生成输出文件名
        output_filename = f"learning_notes_{uuid.uuid4().hex[:8]}.md"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        print("*"*50)
        print(upload_files)
        # head
        content = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # 添加用户输入
        if text and text.strip():
            text_app = AiHelper(mode, "./resource/configuration.json", text)
            content += text_app.generate()
            # 分流输入，提高性能
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(content)

        # 处理上传的文件
        if upload_files:
            for file_path in upload_files:
                file_content = read_file_content(file_path)
                text_app = AiHelper(mode, "./resource/configuration.json", file_content)
                file_reader = text_app.generate()
                with open(output_path, 'a', encoding='utf-8') as f:
                    f.write(file_reader)



        # 写入文件

        return output_path

    except Exception as e:
        error_filename = f"error_{uuid.uuid4().hex[:8]}.txt"
        error_path = os.path.join(app.config['OUTPUT_FOLDER'], error_filename)
        with open(error_path, 'w', encoding='utf-8') as f:
            f.write(f"生成笔记时出错: {str(e)}")
        return error_path


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/submit-request', methods=['POST'])
def submit_request():
    """处理学习请求"""
    try:
        print("收到提交请求")

        # 获取表单数据
        user_input = request.form.get('user_input', '').strip()
        analysis_mode = request.form.get('analysis_mode')

        print(f"用户输入长度: {len(user_input)}")
        print(f"模式: {analysis_mode}")

        # 验证必填字段
        if not user_input and not request.files.getlist('files'):
            return jsonify({
                'success': False,
                'message': '请输入学习内容或上传文件'
            }), 400

        if not analysis_mode:
            return jsonify({
                'success': False,
                'message': '请选择处理模式'
            }), 400

        # 处理上传的文件
        uploaded_file_paths = []
        files = request.files.getlist('files')
        print(f"文件数量: {len(files)}")
        print(f"L110 {files}")
        for file in files:
            if file and file.filename:
                print(f"处理文件: {file.filename}")
                filename = secure_filename(file.filename)
                print(f"L114 {filename}")
                if allowed_file(filename):
                    unique_filename = f"{uuid.uuid4().hex[:8]}.{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

                    # 确保目录存在
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    file.save(file_path)
                    print(f"文件保存到: {file_path}")

                    # 添加到文件路径列表
                    uploaded_file_paths.append(file_path)
                else:
                    print(f"文件类型不支持: {filename}")

        print(f"准备调用 manager 函数")
        print(f"   - 用户输入: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        print(f"   - 文件路径列表: {uploaded_file_paths}")

        # 映射模式到数字
        mode_mapping = {
            'cloud': 0,  # 阿里云
            'local': 1,  # 本地Ollama
            'gpt': 2  # ChatGPT
        }

        mode = mode_mapping.get(analysis_mode, 0)  # 默认阿里云

        # 调用数据处理函数
        print(f"🚀 开始处理请求，模式: {analysis_mode} (代码: {mode})")
        output_file_path = manager(user_input, uploaded_file_paths, mode)

        # 检查输出文件是否存在
        if os.path.exists(output_file_path):
            file_size = os.path.getsize(output_file_path)
            print(f"输出文件创建成功: {output_file_path} ({file_size} 字节)")
        else:
            print(f": {output_file_path}")

        # 返回成功响应
        return jsonify({
            'success': True,
            'message': '笔记生成完成',
            'output_file': os.path.basename(output_file_path),
            'file_size': os.path.getsize(output_file_path) if os.path.exists(output_file_path) else 0
        })

    except Exception as e:
        error_msg = f"处理请求时出错: {str(e)}"
        print(f"ERROR:  {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500


@app.route('/download/<filename>')
def download_file(filename):
    """下载生成的笔记文件"""
    try:
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], safe_filename)

        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404

        download_name = f"学习笔记_{datetime.now().strftime('%Y%m%d_%H%M')}.md"

        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype='text/markdown'
        )

    except Exception as e:
        print(f"下载文件时出错: {e}")
        return jsonify({
            'success': False,
            'message': f'下载文件时出错: {str(e)}'
        }), 500


def main(cache_confirm=True):
    if cache_confirm:
        kill_cache(
            [
                app.config['UPLOAD_FOLDER'],
                app.config['OUTPUT_FOLDER']
            ]
        )
    app.run(debug=False, host='0.0.0.0', port=5000)
    if cache_confirm:
        print("开始清除缓存")
        kill_cache(
            [
                app.config['UPLOAD_FOLDER'],
                app.config['OUTPUT_FOLDER']
            ]
        )
        print("清除缓存成功")
    print("Server is shutdown")


if __name__ == '__main__':
    main()