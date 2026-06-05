"""gRPC Sensor 服务测试"""
import os
import tempfile
from io import BytesIO

import grpc
from django.test import TestCase

from backend.grpc.sensorgrpc_pb2 import DataRequest, HeartRequest, MinioFileChunk
from backend.grpc.sensorgrpc_pb2_grpc import OskitStub, add_OskitServicer_to_server
from backend.grpc.servicer import SensorGrpcServicer
from backend.models.osdeploy.sensor_data import SensorData


class SensorGrpcServicerTest(TestCase):
    """Sensor gRPC 服务单元测试"""

    def setUp(self):
        """启动内存 gRPC 服务器"""
        self.server = grpc.server(grpc.ThreadPoolExecutor(max_workers=1))
        add_OskitServicer_to_server(SensorGrpcServicer(), self.server)
        self.port = self.server.add_insecure_port("localhost:0")
        self.server.start()

        self.channel = grpc.insecure_channel(f"localhost:{self.port}")
        self.stub = OskitStub(self.channel)

    def tearDown(self):
        self.channel.close()
        self.server.stop(0)

    def test_check_heart(self):
        """测试心跳检测"""
        response = self.stub.CheckHeart(HeartRequest())
        self.assertIsNotNone(response)

    def test_push_data(self):
        """测试数据推送"""
        request = DataRequest(
            function="test_func",
            data='{"cpu": 50}',
            time="2026-06-05T12:00:00Z",
        )
        response = self.stub.PushData(request)
        self.assertIsNotNone(response)

        # 验证数据库记录
        sensor_data = SensorData.objects.first()
        self.assertIsNotNone(sensor_data)
        self.assertEqual(sensor_data.function, "test_func")
        self.assertEqual(sensor_data.data, '{"cpu": 50}')
        self.assertEqual(sensor_data.time, "2026-06-05T12:00:00Z")

    def test_upload_file(self):
        """测试文件上传"""
        chunks = [
            MinioFileChunk(data=b"Hello ", filename="test.txt"),
            MinioFileChunk(data=b"World!", filename="test.txt"),
        ]
        response = self.stub.Upload(iter(chunks))
        self.assertEqual(response.message, "File uploaded successfully")

        # 验证文件已写入
        media_dir = tempfile.gettempdir() if not os.path.exists("media") else "media"
        upload_dir = os.path.join(media_dir, "sensor_uploads")
        files = os.listdir(upload_dir)
        self.assertTrue(any(f.endswith("_test.txt") for f in files))

    def test_upload_empty_filename(self):
        """测试空文件名应报错"""
        chunks = [MinioFileChunk(data=b"test", filename="")]
        with self.assertRaises(grpc.RpcError) as cm:
            self.stub.Upload(iter(chunks))
        self.assertEqual(cm.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)

    def test_extract_ip_ipv4(self):
        """测试 IPv4 peer 地址提取"""
        servicer = SensorGrpcServicer()
        self.assertEqual(servicer._extract_ip("ipv4:192.168.1.1:12345"), "192.168.1.1")

    def test_extract_ip_ipv6(self):
        """测试 IPv6 peer 地址提取"""
        servicer = SensorGrpcServicer()
        self.assertEqual(servicer._extract_ip("ipv6:[::1]:12345"), "[::1]")

    def test_extract_ip_unknown(self):
        """测试未知格式 peer 地址提取"""
        servicer = SensorGrpcServicer()
        self.assertEqual(servicer._extract_ip("unknown"), "unknown")