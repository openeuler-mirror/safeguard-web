"""gRPC Sensor 服务实现"""
import os
from datetime import datetime

import grpc

from backend.grpc.sensorgrpc_pb2 import DataReply, HeartReply, MinioUploadResponse
from backend.grpc.sensorgrpc_pb2_grpc import OskitServicer
from backend.models.osdeploy.sensor_data import SensorData
from safeguard_web.settings import MEDIA_ROOT, BASE_DIR


class SensorGrpcServicer(OskitServicer):
    """Sensor gRPC 服务实现"""

    def PushData(self, request, context):
        """接收 agent 推送的数据并写入数据库"""
        try:
            # 获取客户端 IP
            peer = context.peer()
            # peer 格式如 ipv4:127.0.0.1:12345 或 ipv6:[::1]:12345
            client_ip = self._extract_ip(peer)

            SensorData.objects.create(
                ip=client_ip,
                function=request.function,
                data=request.data,
                time=request.time,
            )
            return DataReply()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {e}")
            raise

    def CheckHeart(self, request, context):
        """心跳检测"""
        return HeartReply()

    def Upload(self, request_iterator, context):
        """流式文件上传，保存到本地存储"""
        data = bytearray()
        filename = ""

        for chunk in request_iterator:
            if not filename:
                filename = chunk.filename
            data.extend(chunk.data)

        if not filename:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Filename is empty")
            raise grpc.RpcError("Filename is empty")

        upload_dir = os.path.join(MEDIA_ROOT or str(BASE_DIR / "media"), "sensor_uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # 防止文件名冲突，添加时间戳前缀
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_dir, safe_filename)

        try:
            with open(filepath, "wb") as f:
                f.write(data)
            return MinioUploadResponse(message="File uploaded successfully")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Write file error: {e}")
            raise

    @staticmethod
    def _extract_ip(peer):
        """从 gRPC peer 字符串中提取 IP 地址"""
        # peer 格式: ipv4:127.0.0.1:12345 或 ipv6:[::1]:12345
        if peer.startswith("ipv4:"):
            rest = peer[5:]
            # 去掉端口号
            if ":" in rest:
                return rest.rsplit(":", 1)[0]
            return rest
        if peer.startswith("ipv6:"):
            rest = peer[5:]
            # ipv6 格式: [::1]:12345
            if rest.startswith("[") and "]" in rest:
                return rest[:rest.index("]") + 1]
            return rest
        return peer
