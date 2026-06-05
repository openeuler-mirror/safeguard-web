"""启动 gRPC Sensor 服务"""
from django.core.management.base import BaseCommand
import grpc
from concurrent import futures

from backend.grpc.sensorgrpc_pb2_grpc import add_OskitServicer_to_server
from backend.grpc.servicer import SensorGrpcServicer


class Command(BaseCommand):
    help = "启动 Sensor gRPC 服务器"

    def add_arguments(self, parser):
        parser.add_argument(
            "--host",
            default="0.0.0.0",
            help="绑定地址 (默认: 0.0.0.0)",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=50051,
            help="监听端口 (默认: 50051)",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=10,
            help="线程池工作线程数 (默认: 10)",
        )

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]
        workers = options["workers"]
        address = f"{host}:{port}"

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))
        add_OskitServicer_to_server(SensorGrpcServicer(), server)
        server.add_insecure_port(address)
        server.start()

        self.stdout.write(self.style.SUCCESS(f"gRPC Sensor 服务器已启动: {address}"))
        self.stdout.write("按 Ctrl+C 停止服务")

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            server.stop(0)
            self.stdout.write(self.style.SUCCESS("gRPC Sensor 服务器已停止"))