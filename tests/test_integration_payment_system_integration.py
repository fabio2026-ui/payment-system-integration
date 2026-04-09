import pytest
import requests
import json

class TestIntegration:
    """集成测试类"""
    
    BASE_URL = "http://localhost:8000"
    
    def test_api_health(self):
        """测试API健康检查"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_docs(self):
        """测试API文档"""
        response = requests.get(f"{self.BASE_URL}/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["Content-Type"]
    
    def test_openapi_spec(self):
        """测试OpenAPI规范"""
        response = requests.get(f"{self.BASE_URL}/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert data["openapi"].startswith("3.")
    
    def test_error_responses(self):
        """测试错误响应"""
        # 测试不存在的端点
        response = requests.get(f"{self.BASE_URL}/nonexistent")
        assert response.status_code == 404
    
    def test_rate_limiting(self):
        """测试速率限制"""
        # 这里添加速率限制测试
        # 注意: 在实际测试中需要小心不要触发真实的速率限制
        pass
