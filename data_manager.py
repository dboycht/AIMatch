# -*- coding: utf-8 -*-
"""
AI学习笔记生成器 - 数据处理库
Stu ID: 032530213@NUAA
email: chenghaotian@nuaa.edu.cn
version: 1.0
"""
from os import PathLike
from openai import OpenAI
import shutil
import json
import wave
from vosk import Model, KaldiRecognizer
import docx2txt
import subprocess
import os
import PyPDF2
from pdfminer.high_level import extract_text
import pdfplumber

global converted_path
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'md', 'docx', 'wov', 'mp3', 'm4a']


def read_pdf(pdf_path_in_read_pdf, method='auto'):
    """
    统一的PDF读取函数

    参数:
        pdf_path (str): PDF文件路径
        method (str): 读取方法，可选 'auto', 'pdfplumber', 'pypdf2', 'pdfminer'

    返回:
        str: PDF中的文本内容
    """
    try:
        if not os.path.exists(pdf_path_in_read_pdf):
            return f"错误：文件不存在 - {pdf_path_in_read_pdf}"

        if not pdf_path_in_read_pdf.lower().endswith('.pdf'):
            return "错误：文件格式必须是PDF"

        if method == 'auto' or method == 'pdfplumber':
            try:
                return read_pdf_pdfplumber(pdf_path_in_read_pdf)
            except ImportError:
                if method == 'pdfplumber':
                    return "错误：pdfplumber未安装，请运行: pip install pdfplumber"
                # 自动回退到其他方法
                pass

        if method == 'auto' or method == 'pypdf2':
            try:
                return read_pdf_pypdf2(pdf_path_in_read_pdf)
            except ImportError:
                if method == 'pypdf2':
                    return "错误：PyPDF2未安装，请运行: pip install PyPDF2"
                pass

        if method == 'auto' or method == 'pdfminer':
            try:
                from pdfminer.high_level import extract_text
                return read_pdf_pdfminer(pdf_path_in_read_pdf)
            except ImportError:
                if method == 'pdfminer':
                    return "错误：pdfminer.six未安装，请运行: pip install pdfminer.six"
                pass

        return "错误：没有可用的PDF解析库，请安装 pdfplumber、PyPDF2 或 pdfminer.six"

    except Exception as e:
        return f"读取PDF错误: {e}"


def read_pdf_pdfplumber(pdf_path_hy_w):
    """pdfplumber实现"""
    full_text = []
    with pdfplumber.open(pdf_path_hy_w) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                full_text.append(text)
    return '\n'.join(full_text)


def read_pdf_pypdf2(pdf_path_r_p_pp):
    """PyPDF2实现"""
    full_text = []
    with open(pdf_path_r_p_pp, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text:
                full_text.append(text)
    return '\n'.join(full_text)


def read_pdf_pdfminer(pdf_path_rp_p):
    """pdfminer实现"""
    return extract_text(pdf_path_rp_p)


def read_word_document(file_path):
    """
    读取Word文档（支持.doc和.docx格式）

    参数:
        file_path (str): Word文档路径

    返回:
        str: 文档中的文本内容
    """
    try:
        if not os.path.exists(file_path):
            return f"错误：文件不存在 - {file_path}"

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.docx':
            # 使用docx2txt读取.docx文件
            return read_docx(file_path)

        elif file_ext == '.doc':
            # 使用多种方法尝试读取.doc文件
            return read_doc(file_path)

        else:
            return f"错误：不支持的文件格式 - {file_ext}"

    except Exception as e:
        return f"读取文档错误: {e}"


def read_docx(file_path):
    """读取.docx文件的辅助函数"""
    try:
        text = docx2txt.process(file_path)
        return text.strip() if text.strip() else "文档为空"
    except Exception as e:
        return f"读取.docx文件错误: {e}"


def read_doc(file_path):
    """读取.doc文件的辅助函数"""
    try:
        result = subprocess.run(
            ['catdoc', '-w', file_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            check=True
        )
        text = result.stdout.strip()
        if text:
            return text

    except Exception as e:
        return f"读取文档错误: {e}"

    # 尝试使用antiword
    try:
        result = subprocess.run(
            ['antiword', file_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            check=True
        )
        text = result.stdout.strip()
        if text:
            return text

    except Exception as e:
        return f"读取文档错误: {e}"

    return "请安装cat doc"



def ensure_audio_format(file_path):
    try:
        temp_path = "temp_audio.wav"

        # 使用ffmpeg转换音频格式
        cmd = [
            'ffmpeg', '-i', file_path,
            '-acodec', 'pcm_s16le',  # 16位PCM编码
            '-ac', '1',  # 单声道
            '-ar', '16000',  # 16kHz采样率
            '-y',  # 覆盖输出文件
            temp_path
        ]

        # 运行转换命令
        result_1 = subprocess.run(cmd, capture_output=True, text=True)

        if result_1.returncode == 0:
            return temp_path
        else:
            print(f"音频转换失败: {result_1.stderr}")
            return None

    except Exception as e:
        print(f"格式转换错误: {e}")
        return None

def vosk_speech_to_text_improved(file_path, model_path="vosk-model-cn-0.22"):
    """
    改进的Vosk语音识别函数

    参数:
        file_path (str): 音频文件路径
        model_path (str): Vosk模型路径

    返回:
        str: 识别出的文本内容
    """
    converted_path_112 = ""
    try:
        converted_path_112 = ensure_audio_format(file_path)
        if not converted_path_112:
            return "错误：音频格式转换失败"
        model = Model(model_path)
        wf = wave.open(converted_path_112, 'rb')
        print(f"音频信息: {wf.getnchannels()}声道, {wf.getsampwidth()}字节/样本, {wf.getframerate()}Hz采样率")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        results = []
        chunk_size = 4000
        while True:
            data = wf.readframes(chunk_size)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result_ = json.loads(rec.Result())
                text = result_.get('text', '').strip()
                if text:
                    text = text.replace(" ", '')
                    results.append(text)
                    print(f"识别到: {text}")
        final_result = json.loads(rec.FinalResult())
        final_text = final_result.get('text', '').strip()
        if final_text:
            results.append(final_text)
            print(f"最终识别: {final_text}")
        wf.close()
        if os.path.exists(converted_path_112):
            os.remove(converted_path_112)
        combined_text = ', '.join(results)
        return combined_text if combined_text else "未识别到内容"

    except Exception as e:
        if 'converted_path' in locals() and converted_path_112 and os.path.exists(converted_path_112):
            os.remove(converted_path_112)
        return f"识别错误: {e}"


# TXT
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    print(f"L86: {filename}")
    return filename.lower().strip().rsplit(".")[-1] in ALLOWED_EXTENSIONS


def read_file_content(file_path: str):
    """
    read files with types
    :param file_path: the path
    :return: content
    """
    try:
        end = file_path.rsplit('.')[-1].lower()
        if end in ['txt', 'md']:
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            return "无法读取文件内容（编码问题）"
        elif end in ['mp3', 'wov', 'm4a']:
            return vosk_speech_to_text_improved(file_path)
        elif end in ['doc', 'docx']:
            if end == 'doc':
                return read_doc(file_path)
            else:
                return read_docx(file_path)
        elif end == 'pdf':
            return read_pdf(file_path, method='auto')
        elif end in ['jpg', 'jpeg', 'png']:
            return "pass"
        else:
            return f"文件类型暂不支持直接读取: {os.path.basename(file_path)}"
    except Exception as e:
        return f"读取文件时出错: {str(e)}"


def req(system_: str, user_: str, client_: OpenAI, model_: str):
    """

    :param system_:
    :param user_:
    :param client_:
    :param model_:
    :return:
    """
    print("\nThinking...")
    messages_ = [{
        "role": "system",
        "content": system_
    }, {
        "role": "user",
        "content": user_
    }
    ]

    if model_ == "qwen-plus":
        # 针对阿里云API优化
        completion = client_.chat.completions.create(
            model="qwen-plus",  # 您可以按需更换为其它深度思考模型
            messages=messages_,
            extra_body={"enable_thinking": True},
            stream=True
        )
        answer_content = ""  # 完整回复
        reasoning_content = ""
        is_answering_ = False
        for chunk in completion:
            if not chunk.choices:
                print("\nUsage:")
                print(chunk.usage)
                continue

            delta = chunk.choices[0].delta

            # 只收集思考内容
            if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                if not is_answering_:
                    print(delta.reasoning_content, end="", flush=True)
                reasoning_content += delta.reasoning_content

            # 收到content，开始进行回复
            if hasattr(delta, "content") and delta.content:
                if not is_answering_:
                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering_ = True
                print(delta.content, end="")
                answer_content += delta.content
        return answer_content.strip()
    else:
        main_req = client_.chat.completions.create(
            messages=messages_,
            model=model_
        )
        print("生成完成")
        return main_req.choices[0].message.content.strip()


class AiHelper(object):
    def __init__(self, mode:int, conf:PathLike[str]|str, notes:str):

        if mode == 0:
            self.client = OpenAI(
                api_key=os.environ["aliyun_api"],
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            self.model = "qwen-plus"
        elif mode == 1:
            self.client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="wo"
            )
            self.model = "deepseek-r1:8b"
        else:
            self.client = OpenAI(
                api_key=os.environ["openai_api"]
            )
            self.model="gpt-4o-mini"


        self.conf = open(conf, "r", encoding='utf-8')
        self.conf_j = json.load(self.conf)
        self.notes_user = notes

    def generate(self):
        req_note = req(self.conf_j["生成笔记"],self.notes_user ,self.client, self.model)
        return req_note


def clear_folder(folder_path, delete_subfolders=True, confirm=True):
    """
    删除文件夹内内容
    :param folder_path: 文件夹路径
    :param delete_subfolders: 是否删除子文件夹
    :param confirm: 确认与否
    :return: 删除成功与否
    """
    try:
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return False
        items = os.listdir(folder_path)
        if not items:
            return True
        if confirm:
            print(f"文件夹 '{folder_path}' 中包含 {len(items)} 个项目")

        deleted_count = 0
        for item in items:
            item_path = os.path.join(folder_path, item)

            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                    deleted_count += 1
                elif os.path.isdir(item_path) and delete_subfolders:
                    shutil.rmtree(item_path)
                    deleted_count += 1
            except Exception as e:
                print(f"删除 '{item}' 失败: {str(e)}")

        print(f"成功删除 {deleted_count} 个项目")
        return True

    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False


def kill_cache(folder_path_list:list[PathLike[str]]):
    if folder_path_list:
        for killer in folder_path_list:
            clear_folder(killer)
        return 1
    else:
        return 0


if __name__ == '__main__':
    # app = AiHelper(1, "./resource/configuration.json", input("->"))
    # a = vosk_speech_to_text_improved("111.mp3")
    print("何意味？")
