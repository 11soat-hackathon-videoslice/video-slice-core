"""Testes para a interface VdscExceptionHandlerInterface"""
from typing import Callable

import pytest

from core.interfaces.vdsc_exception_handler_interface import VdscExceptionHandlerInterface


@pytest.mark.unit
class TestVdscExceptionHandlerInterface:
    """Testes para VdscExceptionHandlerInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            VdscExceptionHandlerInterface()

    def test_interface_has_vdsc_exception_handler_method(self):
        """Testa que a interface tem o método vdsc_exception_handler"""
        assert hasattr(VdscExceptionHandlerInterface, 'vdsc_exception_handler')

    def test_concrete_implementation_handler(self):
        """Testa implementação concreta do handler"""

        class ConcreteExceptionHandler(VdscExceptionHandlerInterface):
            def __init__(self):
                self.handled_exceptions = []

            def vdsc_exception_handler(self, func: Callable) -> Callable:
                def wrapper(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        self.handled_exceptions.append(e)
                        raise
                return wrapper

        handler = ConcreteExceptionHandler()

        @handler.vdsc_exception_handler
        def test_function():
            raise ValueError("Test exception")

        with pytest.raises(ValueError):
            test_function()

        assert len(handler.handled_exceptions) == 1
        assert isinstance(handler.handled_exceptions[0], ValueError)
        assert str(handler.handled_exceptions[0]) == "Test exception"

    def test_handler_preserves_function_return_value(self):
        """Testa que o handler preserva o valor de retorno da função"""

        class ConcreteExceptionHandler(VdscExceptionHandlerInterface):
            def vdsc_exception_handler(self, func: Callable) -> Callable:
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper

        handler = ConcreteExceptionHandler()

        @handler.vdsc_exception_handler
        def test_function(x, y):
            return x + y

        result = test_function(5, 3)
        assert result == 8

    def test_handler_with_arguments(self):
        """Testa handler com argumentos na função decorada"""

        class ConcreteExceptionHandler(VdscExceptionHandlerInterface):
            def vdsc_exception_handler(self, func: Callable) -> Callable:
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper

        handler = ConcreteExceptionHandler()

        @handler.vdsc_exception_handler
        def test_function(event, config):
            return {"event": event, "config": config}

        result = test_function("test_event", {"key": "value"})
        assert result["event"] == "test_event"
        assert result["config"] == {"key": "value"}

    def test_handler_with_kwargs(self):
        """Testa handler com keyword arguments"""

        class ConcreteExceptionHandler(VdscExceptionHandlerInterface):
            def vdsc_exception_handler(self, func: Callable) -> Callable:
                def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)
                return wrapper

        handler = ConcreteExceptionHandler()

        @handler.vdsc_exception_handler
        def test_function(**kwargs):
            return kwargs

        result = test_function(video_id="123", user_id="456")
        assert result["video_id"] == "123"
        assert result["user_id"] == "456"

    def test_handler_multiple_exceptions(self):
        """Testa handler capturando múltiplas exceções diferentes"""

        class ConcreteExceptionHandler(VdscExceptionHandlerInterface):
            def __init__(self):
                self.exceptions = []

            def vdsc_exception_handler(self, func: Callable) -> Callable:
                def wrapper(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        self.exceptions.append(e)
                        raise
                return wrapper

        handler = ConcreteExceptionHandler()

        @handler.vdsc_exception_handler
        def test_function(error_type):
            if error_type == "value":
                raise ValueError("Value error")
            elif error_type == "key":
                raise KeyError("Key error")
            elif error_type == "type":
                raise TypeError("Type error")

        errors = ["value", "key", "type"]
        for error_type in errors:
            with pytest.raises(Exception):
                test_function(error_type)

        assert len(handler.exceptions) == 3
        assert isinstance(handler.exceptions[0], ValueError)
        assert isinstance(handler.exceptions[1], KeyError)
        assert isinstance(handler.exceptions[2], TypeError)

