/*
* 网页后端JavaScript
* author: Chenghaotian
* version: 1.0
* 11.3 修复重复下载的bug
* */
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const form = document.getElementById('ai-assistant-form');
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const submitBtn = document.getElementById('submit-btn');
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');
    const autoDownloadBtn = document.getElementById('auto-download-btn');
    const newRequestBtn = document.getElementById('new-request-btn');
    const analysisMode = document.getElementById('analysis-mode');

    // 存储上传的文件
    let uploadedFiles = [];
    let currentOutputFile = null;

    // 初始化事件监听
    initEventListeners();

    function initEventListeners() {
        // 文件上传区域点击事件
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });

        // 拖拽上传功能
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.style.borderColor = '#4361ee';
            uploadArea.style.backgroundColor = '#e9f7fe';
        });

        uploadArea.addEventListener('dragleave', function() {
            uploadArea.style.borderColor = '#ced4da';
            uploadArea.style.backgroundColor = '#f8f9fa';
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.style.borderColor = '#ced4da';
            uploadArea.style.backgroundColor = '#f8f9fa';

            const files = e.dataTransfer.files;
            handleFiles(files);
        });

        // 文件选择变化事件
        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        // 表单提交事件
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitForm();
        });

        // 自动下载按钮
        autoDownloadBtn.addEventListener('click', function() {
            if (currentOutputFile) {
                downloadFile(currentOutputFile);
            }
        });

        // 新建请求按钮
        newRequestBtn.addEventListener('click', function() {
            resetForm();
        });

        // 实时验证表单
        document.getElementById('user-input').addEventListener('input', validateForm);
        analysisMode.addEventListener('change', validateForm);
    }

    function handleFiles(files) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            // 检查文件大小（最大10MB）
            // TODO 支持更大文件
            if (file.size > 10 * 1024 * 1024) {
                showAlert(`文件 "${file.name}" 超过10MB大小限制`, 'warning');
                continue;
            }

            // 检查是否已存在同名文件
            if (isFileAlreadyUploaded(file.name)) {
                showAlert(`文件 "${file.name}" 已经上传过了`, 'info');
                continue;
            }

            uploadedFiles.push(file);
            addFileToList(file, uploadedFiles.length - 1);
        }

        updateFileListEvents();
        validateForm();
    }

    function isFileAlreadyUploaded(filename) {
        return uploadedFiles.some(file => file.name === filename);
    }

    function addFileToList(file, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-name">
                <i class="fas fa-file-alt file-icon"></i>
                <span>${file.name}</span>
                <span class="file-badge">${formatFileSize(file.size)}</span>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger remove-file" data-index="${index}">
                <i class="fas fa-times"></i>
            </button>
        `;

        fileList.appendChild(fileItem);
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function updateFileListEvents() {
        // 添加删除文件事件
        document.querySelectorAll('.remove-file').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                removeFile(index);
            });
        });
    }

    function removeFile(index) {
        if (index >= 0 && index < uploadedFiles.length) {
            uploadedFiles.splice(index, 1);

            // 重新渲染文件列表
            fileList.innerHTML = '';
            uploadedFiles.forEach((file, i) => {
                addFileToList(file, i);
            });

            updateFileListEvents();
            validateForm();
        }
    }

    function validateForm() {
        const userInput = document.getElementById('user-input').value;
        const hasFiles = uploadedFiles.length > 0;
        const hasMode = analysisMode.value;

        // 启用提交按钮的条件：有用户输入或上传了文件，并且选择了模式
        submitBtn.disabled = !((userInput.trim() || hasFiles) && hasMode);
    }

    function submitForm() {
        // 验证表单
        const userInput = document.getElementById('user-input').value;
        const analysisModeValue = analysisMode.value;

        if (!userInput.trim() && uploadedFiles.length === 0) {
            showAlert('请输入学习内容或上传文件！', 'warning');
            return;
        }

        if (!analysisModeValue) {
            showAlert('请选择处理模式！', 'warning');
            return;
        }

        // 显示加载状态
        setLoadingState(true);

        // 创建 FormData 对象
        const formData = new FormData();
        formData.append('user_input', userInput);
        formData.append('analysis_mode', analysisModeValue);

        // 添加上传的文件
        uploadedFiles.forEach(file => {
            formData.append('files', file);
        });

        // 发送请求到后端
        fetch('/submit-request', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP Error-Line 207: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // 保存输出文件名
                    currentOutputFile = data.output_file;

                    // 显示成功结果
                    showResult(data);

                    // 自动下载文件 - 修复部分
                    setTimeout(() => {
                        downloadFile(currentOutputFile);
                    }, 1000); // 延迟1秒确保页面已经更新
                } else {
                    throw new Error(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('提交请求时出错: ' + error.message, 'error');
            })
            .finally(() => {
                setLoadingState(false);
            });
    }

    function setLoadingState(isLoading) {
        if (isLoading) {
            form.style.display = 'none';
            loadingSection.style.display = 'block';
            resultSection.style.display = 'none';
        } else {
            loadingSection.style.display = 'none';
        }
    }

    function showResult(data) {
        resultSection.style.display = 'block';

        // TODO 添加更多结果信息显示
        console.log('处理结果:', data);
    }

    function downloadFile(filename) {
        // 创建隐藏的iframe来触发下载，避免页面跳转
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = `/download/${filename}`;
        document.body.appendChild(iframe);

        // 延迟移除iframe
        setTimeout(() => {
            document.body.removeChild(iframe);
        }, 5000);

        // 同时使用传统方法作为备用
        // window.open(`/download/${filename}`, '_blank');
        // bug已修复
    }

    function resetForm() {
        // 重置表单
        form.reset();
        uploadedFiles = [];
        fileList.innerHTML = '';
        currentOutputFile = null;

        // 显示表单，隐藏结果
        form.style.display = 'block';
        resultSection.style.display = 'none';

        // 重新验证
        validateForm();
    }

    function showAlert(message, type = 'info') {
        // 创建提示元素
        const alert = document.createElement('div');
        alert.className = `alert alert-${getAlertClass(type)} alert-dismissible fade show`;
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            min-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;
        alert.innerHTML = `
            <i class="fas ${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // 5秒后自动移除
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    function getAlertClass(type) {
        switch(type) {
            case 'success': return 'success';
            case 'warning': return 'warning';
            case 'error': return 'danger';
            case 'info':
            default: return 'info';
        }
    }

    function getAlertIcon(type) {
        switch(type) {
            case 'success': return 'fa-check-circle';
            case 'warning': return 'fa-exclamation-triangle';
            case 'error': return 'fa-times-circle';
            case 'info':
            default: return 'fa-info-circle';
        }
    }

    // 初始化表单验证
    validateForm();
});