"""
统一的 ViewSet 基类
确保所有 API 响应都使用统一格式 {errno, errmsg, data}
"""
from rest_framework import viewsets
from rest_framework.response import Response
from backend.common import SuccessResponse, ErrorResponse, ErrCode


class UnifiedModelViewSet(viewsets.ModelViewSet):
    """
    统一响应格式的 ModelViewSet
    list/retrieve 返回 {errno, errmsg, data}
    create/update/partial_update/destroy 成功时返回 {errno, errmsg, data}
    """

    def list(self, request, *args, **kwargs):
        """列表操作"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return SuccessResponse({'results': serializer.data, 'count': self.paginator.count})
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse({'results': serializer.data, 'count': len(serializer.data)})

    def retrieve(self, request, *args, **kwargs):
        """详情操作"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(serializer.data)

    def create(self, request, *args, **kwargs):
        """创建操作"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return SuccessResponse(serializer.data)

    def update(self, request, *args, **kwargs):
        """更新操作"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return SuccessResponse(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """部分更新操作"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除操作"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return SuccessResponse(errmsg='删除成功')
