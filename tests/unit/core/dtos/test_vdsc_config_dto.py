"""Testes unitários para VdscConfigDTO e classes relacionadas"""
import pytest
from core.dtos.vdsc_config_dto import (
    ResizeDTO,
    ScheduleRulesDTO,
    VdscSettingsDTO,
    VdscConfigDTO
)

@pytest.mark.unit
class TestResizeDTO:
    """Testes para a classe ResizeDTO"""

    def test_create_quality_dto(self):
        """Testa criação de ResizeDTO com valores válidos"""
        resize = ResizeDTO(
            ultra=2160,
            high=1080,
            medium=720,
            low=480
        )

        assert resize.ultra == 2160
        assert resize.high == 1080
        assert resize.medium == 720
        assert resize.low == 480

    def test_quality_dto_is_immutable(self):
        """Testa que ResizeDTO é imutável (frozen)"""
        resize = ResizeDTO(
            ultra=2160,
            high=1080,
            medium=720,
            low=480
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            resize.high = 1920

    def test_quality_dto_equality(self):
        """Testa comparação de igualdade entre instâncias"""
        quality1 = ResizeDTO(ultra=2160, high=1080, medium=720, low=480)
        quality2 = ResizeDTO(ultra=2160, high=1080, medium=720, low=480)
        quality3 = ResizeDTO(ultra=1920, high=1080, medium=720, low=480)

        assert quality1 == quality2
        assert quality1 != quality3

    def test_quality_dto_with_zero_values(self):
        """Testa criação com valores zero"""
        resize = ResizeDTO(ultra=0, high=0, medium=0, low=0)

        assert resize.ultra == 0
        assert resize.high == 0
        assert resize.medium == 0
        assert resize.low == 0

    def test_quality_dto_with_negative_values(self):
        """Testa criação com valores negativos"""
        resize = ResizeDTO(ultra=-1, high=-1, medium=-1, low=-1)

        assert resize.ultra == -1
        assert resize.high == -1
        assert resize.medium == -1
        assert resize.low == -1


@pytest.mark.unit
class TestScheduleRulesDTO:
    """Testes para a classe ScheduleRulesDTO"""

    def test_create_schedule_rules_dto(self):
        """Testa criação de ScheduleRulesDTO com valores válidos"""
        rules = ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )

        assert rules.retry_backoff_factor == 2
        assert rules.retry_arn == "arn:aws:scheduler:us-east-1:123456789012:schedule/retry"
        assert rules.retry_role_arn == "arn:aws:iam::123456789012:role/scheduler-role"
        assert rules.retry_dlq == "arn:aws:sqs:us-east-1:123456789012:queue/dlq"

    def test_schedule_rules_dto_is_immutable(self):
        """Testa que ScheduleRulesDTO é imutável (frozen)"""
        rules = ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            rules.retry_backoff_factor = 3

    def test_schedule_rules_dto_equality(self):
        """Testa comparação de igualdade entre instâncias"""
        rules1 = ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )
        rules2 = ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )
        rules3 = ScheduleRulesDTO(
            retry_backoff_factor=3,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )

        assert rules1 == rules2
        assert rules1 != rules3

    def test_schedule_rules_dto_with_empty_strings(self):
        """Testa criação com strings vazias"""
        rules = ScheduleRulesDTO(
            retry_backoff_factor=0,
            retry_arn="",
            retry_role_arn="",
            retry_dlq=""
        )

        assert rules.retry_arn == ""
        assert rules.retry_role_arn == ""
        assert rules.retry_dlq == ""

    def test_to_dict_with_all_attributes(self):
        # Arrange
        dto = ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:events:us-east-1:123456789012:rule/retry-rule",
            retry_role_arn="arn:aws:iam::123456789012:role/retry-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:retry-dlq"
        )

        # Act
        result = dto.to_dict()

        # Assert
        expected = {
            'retry_backoff_factor': 2,
            'retry_arn': "arn:aws:events:us-east-1:123456789012:rule/retry-rule",
            'retry_role_arn': "arn:aws:iam::123456789012:role/retry-role",
            'retry_dlq': "arn:aws:sqs:us-east-1:123456789012:retry-dlq"
        }
        assert result == expected
        assert isinstance(result, dict)

    def test_to_dict_without_all_attributes(self):
        # Arrange
        dto = ScheduleRulesDTO(
            retry_backoff_factor=0,
            retry_arn="",
            retry_role_arn="",
            retry_dlq=""
        )

        # Act
        result = dto.to_dict()

        # Assert
        expected = {
            'retry_backoff_factor': 0,
            'retry_arn': "",
            'retry_role_arn': "",
            'retry_dlq': ""
        }
        assert result == expected


@pytest.mark.unit
class TestVdscSettingsDTO:
    """Testes para a classe VdscSettingsDTO"""

    @pytest.fixture
    def quality_dto(self):
        """Fixture com ResizeDTO válido"""
        return ResizeDTO(ultra=2160, high=1080, medium=720, low=480)

    @pytest.fixture
    def schedule_rules_dto(self):
        """Fixture com ScheduleRulesDTO válido"""
        return ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )

    @pytest.fixture
    def vdsc_settings_dto(self, quality_dto, schedule_rules_dto):
        """Fixture com VdscSettingsDTO válido"""
        return VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

    def test_create_vdsc_settings_dto(self, quality_dto, schedule_rules_dto):
        """Testa criação de VdscSettingsDTO com valores válidos"""
        settings = VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

        assert settings.dir_uploads == "uploads/"
        assert settings.dir_finished == "finished/"
        assert settings.dir_tmp == "tmp/"
        assert settings.max_workers ==  10
        assert settings.resize == quality_dto
        assert settings.schedule_event_rules == schedule_rules_dto

    def test_vdsc_settings_dto_is_immutable(self, quality_dto, schedule_rules_dto):
        """Testa que VdscSettingsDTO é imutável (frozen)"""
        settings = VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            settings.max_workers = 5

    def test_vdsc_settings_dto_equality(self, quality_dto, schedule_rules_dto):
        """Testa comparação de igualdade entre instâncias"""
        settings1 = VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )
        settings2 = VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )
        settings3 = VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=ResizeDTO(ultra=1920, high=1080, medium=720, low=480),
            schedule_event_rules=schedule_rules_dto
        )

        assert settings1 == settings2
        assert settings1 != settings3

    def test_vdsc_settings_dto_access_nested_properties(self, quality_dto, schedule_rules_dto):
        """Testa acesso a propriedades aninhadas"""
        settings = VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

        assert settings.resize.high == 1080
        assert settings.schedule_event_rules.retry_backoff_factor == 2



@pytest.mark.unit
class TestVdscConfigDTO:
    """Testes para a classe VdscConfigDTO"""

    @pytest.fixture
    def quality_dto(self):
        """Fixture com ResizeDTO válido"""
        return ResizeDTO(ultra=2160, high=1080, medium=720, low=480)

    @pytest.fixture
    def schedule_rules_dto(self):
        """Fixture com ScheduleRulesDTO válido"""
        return ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )

    @pytest.fixture
    def vdsc_settings_dto(self, quality_dto, schedule_rules_dto):
        """Fixture com VdscSettingsDTO válido"""
        return VdscSettingsDTO(
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_tmp="tmp/",
            max_workers=10,
            resize=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

    def test_create_vdsc_config_dto(self, vdsc_settings_dto):
        """Testa criação de VdscConfigDTO com valores válidos"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="my-video-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=vdsc_settings_dto
        )

        assert config.aws_region == "us-east-1"
        assert config.s3_bucket_name == "my-video-bucket"
        assert config.dynamodb_table_name == "VideoSlice"
        assert config.event_bus_name == "video-slice-events"
        assert config.vdsc == vdsc_settings_dto

    def test_vdsc_config_dto_is_immutable(self, vdsc_settings_dto):
        """Testa que VdscConfigDTO é imutável (frozen)"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="my-video-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=vdsc_settings_dto
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.aws_region = "us-west-2"  # type: ignore

    def test_vdsc_config_dto_equality(self, vdsc_settings_dto):
        """Testa comparação de igualdade entre instâncias"""
        config1 = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="my-video-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=vdsc_settings_dto
        )
        config2 = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="my-video-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=vdsc_settings_dto
        )
        config3 = VdscConfigDTO(
            aws_region="us-west-2",
            s3_bucket_name="my-video-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=vdsc_settings_dto
        )

        assert config1 == config2
        assert config1 != config3

    def test_vdsc_config_dto_access_nested_properties(self, vdsc_settings_dto):
        """Testa acesso a propriedades profundamente aninhadas"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="my-video-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=vdsc_settings_dto
        )

        assert config.vdsc.resize.high == 1080
        assert config.vdsc.schedule_event_rules.retry_backoff_factor == 2

    def test_vdsc_config_dto_with_different_regions(self, vdsc_settings_dto):
        """Testa criação com diferentes regiões AWS"""
        regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

        for region in regions:
            config = VdscConfigDTO(
                aws_region=region,
                s3_bucket_name="my-video-bucket",
                dynamodb_table_name="VideoSlice",
                event_bus_name="video-slice-events",
                vdsc=vdsc_settings_dto
            )
            assert config.aws_region == region

    def test_vdsc_config_dto_complete_structure(self):
        """Testa criação completa de toda a hierarquia de DTOs"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="my-video-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=VdscSettingsDTO(
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_tmp="tmp/",
                max_workers=10,
                resize=ResizeDTO(
                    ultra=2160,
                    high=1080,
                    medium=720,
                    low=480
                ),
                schedule_event_rules=ScheduleRulesDTO(
                    retry_backoff_factor=2,
                    retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
                    retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
                    retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
                )
            )
        )

        # Verifica toda a estrutura
        assert config.aws_region == "us-east-1"
        assert config.s3_bucket_name == "my-video-bucket"
        assert config.dynamodb_table_name == "VideoSlice"
        assert config.event_bus_name == "video-slice-events"
        assert config.vdsc.resize.high == 1080
        assert config.vdsc.schedule_event_rules.retry_backoff_factor == 2

    def test_vdsc_config_dto_with_empty_strings(self, vdsc_settings_dto):
        """Testa criação com strings vazias"""
        config = VdscConfigDTO(
            aws_region="",
            s3_bucket_name="",
            dynamodb_table_name="",
            event_bus_name="",
            vdsc=vdsc_settings_dto
        )

        assert config.aws_region == ""
        assert config.s3_bucket_name == ""
        assert config.dynamodb_table_name == ""
        assert config.event_bus_name == ""


@pytest.mark.unit
class TestVdscConfigDTOIntegration:
    """Testes de integração para VdscConfigDTO"""

    def test_full_config_creation_and_access(self):
        """Testa criação e acesso completo de configuração"""
        # Cria configuração completa
        config = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="vdsc-prd-s3-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=VdscSettingsDTO(
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_tmp="tmp/",
                max_workers=10,
                resize=ResizeDTO(ultra=2160, high=1080, medium=720, low=480),
                schedule_event_rules=ScheduleRulesDTO(
                    retry_backoff_factor=2,
                    retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/vdsc-retry",
                    retry_role_arn="arn:aws:iam::123456789012:role/vdsc-scheduler-role",
                    retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/vdsc-dlq"
                )
            )
        )

        # Testa acesso a todos os níveis
        assert config.aws_region == "us-east-1"
        assert config.s3_bucket_name == "vdsc-prd-s3-bucket"
        assert config.vdsc.max_workers == 10
        assert config.vdsc.resize.ultra == 2160
        assert config.vdsc.resize.high == 1080
        assert config.vdsc.resize.medium == 720
        assert config.vdsc.resize.low == 480
        assert config.vdsc.schedule_event_rules.retry_backoff_factor == 2
        assert "vdsc-retry" in config.vdsc.schedule_event_rules.retry_arn

    def test_config_immutability_at_all_levels(self):
        """Testa imutabilidade em todos os níveis da hierarquia"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="my-bucket",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            vdsc=VdscSettingsDTO(
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_tmp="tmp/",
                max_workers=10,
                resize=ResizeDTO(ultra=2160, high=1080, medium=720, low=480),
                schedule_event_rules=ScheduleRulesDTO(
                    retry_backoff_factor=2,
                    retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
                    retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
                    retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
                )
            )
        )

        # Testa imutabilidade em cada nível
        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.aws_region = "us-west-2"  # type: ignore


        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.vdsc.max_workers = 5  # type: ignore

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.vdsc.resize.high = 1920  # type: ignore

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.vdsc.schedule_event_rules.retry_backoff_factor = 3  # type: ignore

    def test_multiple_configs_independence(self):
        """Testa que múltiplas configurações são independentes"""
        config1 = VdscConfigDTO(
            aws_region="us-east-1",
            s3_bucket_name="bucket1",
            dynamodb_table_name="VideoSlice1",
            event_bus_name="events1",
            vdsc=VdscSettingsDTO(
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_tmp="tmp/",
                max_workers=10,
                resize=ResizeDTO(ultra=2160, high=1080, medium=720, low=480),
                schedule_event_rules=ScheduleRulesDTO(
                    retry_backoff_factor=2,
                    retry_arn="arn1",
                    retry_role_arn="role1",
                    retry_dlq="dlq1"
                )
            )
        )

        config2 = VdscConfigDTO(
            aws_region="us-west-2",
            s3_bucket_name="bucket2",
            dynamodb_table_name="VideoSlice2",
            event_bus_name="events2",
            vdsc=VdscSettingsDTO(
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_tmp="tmp/",
                max_workers=10,
                resize=ResizeDTO(ultra=1920, high=720, medium=480, low=360),
                schedule_event_rules=ScheduleRulesDTO(
                    retry_backoff_factor=3,
                    retry_arn="arn2",
                    retry_role_arn="role2",
                    retry_dlq="dlq2"
                )
            )
        )

        # Verifica que as configurações são independentes
        assert config1.aws_region != config2.aws_region
        assert config1.s3_bucket_name != config2.s3_bucket_name
        assert config1.dynamodb_table_name != config2.dynamodb_table_name
        assert config1.vdsc.resize.high != config2.vdsc.resize.high
