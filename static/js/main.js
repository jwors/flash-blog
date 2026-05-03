// 主 JavaScript 文件

// 表单验证增强
document.addEventListener('DOMContentLoaded', function() {
    // 为所有表单添加提交动画
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 处理中...';
            }
        });
    });

    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });
});

// 文章删除确认
function confirmDelete(postId) {
    if (confirm('确定要删除这篇文章吗？此操作不可恢复！')) {
        fetch('/api/posts/' + postId, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.detail) {
                alert('删除成功！');
                window.location.href = '/';
            } else {
                alert('删除失败：' + (data.detail || '未知错误'));
            }
        })
        .catch(error => {
            alert('请求失败：' + error);
        });
    }
}

// 评论回复表单显示
function showReplyForm(commentId) {
    const form = document.getElementById('reply-form-' + commentId);
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }
}

// 文章内容 Markdown 渲染（后续实现）
function renderMarkdown(content) {
    // TODO: 集成 Markdown 解析库
    return content;
}

// 时间格式化
function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = (now - date) / 1000;

    if (diff < 60) return '刚刚';
    if (diff < 3600) return Math.floor(diff / 60) + '分钟前';
    if (diff < 86400) return Math.floor(diff / 3600) + '小时前';
    if (diff < 2592000) return Math.floor(diff / 86400) + '天前';

    return date.toLocaleDateString('zh-CN');
}