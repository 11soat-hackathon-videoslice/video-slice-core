"""Testes unitários para VdscConfigDTO e classes relacionadas"""
import pytest
from core.dtos.vdsc_config_dto import (
    QualityDTO,
    ScheduleRulesDTO,
    VdscSettingsDTO,
    S3ConfigDTO,
    VdscConfigDTO
)


@pytest.mark.unit
class TestQualityDTO:
    """Testes para a classe QualityDTO"""

    def test_create_quality_dto(self):
        """Testa criação de QualityDTO com valores válidos"""
        quality = QualityDTO(
            ultra=2160,
            high=1080,
            medium=720,
            low=480
        )

        assert quality.ultra == 2160
        assert quality.high == 1080
        assert quality.medium == 720
        assert quality.low == 480

    def test_quality_dto_is_immutable(self):
        """Testa que QualityDTO é imutável (frozen)"""
        quality = QualityDTO(
            ultra=2160,
            high=1080,
            medium=720,
            low=480
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            quality.high = 1920

    def test_quality_dto_equality(self):
        """Testa comparação de igualdade entre instâncias"""
        quality1 = QualityDTO(ultra=2160, high=1080, medium=720, low=480)
        quality2 = QualityDTO(ultra=2160, high=1080, medium=720, low=480)
        quality3 = QualityDTO(ultra=1920, high=1080, medium=720, low=480)

        assert quality1 == quality2
        assert quality1 != quality3

    def test_quality_dto_with_zero_values(self):
        """Testa criação com valores zero"""
        quality = QualityDTO(ultra=0, high=0, medium=0, low=0)

        assert quality.ultra == 0
        assert quality.high == 0
        assert quality.medium == 0
        assert quality.low == 0

    def test_quality_dto_with_negative_values(self):
        """Testa criação com valores negativos"""
        quality = QualityDTO(ultra=-1, high=-1, medium=-1, low=-1)

        assert quality.ultra == -1
        assert quality.high == -1
        assert quality.medium == -1
        assert quality.low == -1


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
        """Fixture com QualityDTO válido"""
        return QualityDTO(ultra=2160, high=1080, medium=720, low=480)

    @pytest.fixture
    def schedule_rules_dto(self):
        """Fixture com ScheduleRulesDTO válido"""
        return ScheduleRulesDTO(
            retry_backoff_factor=2,
            retry_arn="arn:aws:scheduler:us-east-1:123456789012:schedule/retry",
            retry_role_arn="arn:aws:iam::123456789012:role/scheduler-role",
            retry_dlq="arn:aws:sqs:us-east-1:123456789012:queue/dlq"
        )

    def test_create_vdsc_settings_dto(self, quality_dto, schedule_rules_dto):
        """Testa criação de VdscSettingsDTO com valores válidos"""
        settings = VdscSettingsDTO(
            png_compression_level=3,
            zip_compression_level=6,
            quality=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

        assert settings.png_compression_level == 3
        assert settings.zip_compression_level == 6
        assert settings.quality == quality_dto
        assert settings.schedule_event_rules == schedule_rules_dto

    def test_vdsc_settings_dto_is_immutable(self, quality_dto, schedule_rules_dto):
        """Testa que VdscSettingsDTO é imutável (frozen)"""
        settings = VdscSettingsDTO(
            png_compression_level=3,
            zip_compression_level=6,
            quality=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            settings.png_compression_level = 5

    def test_vdsc_settings_dto_equality(self, quality_dto, schedule_rules_dto):
        """Testa comparação de igualdade entre instâncias"""
        settings1 = VdscSettingsDTO(
            png_compression_level=3,
            zip_compression_level=6,
            quality=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )
        settings2 = VdscSettingsDTO(
            png_compression_level=3,
            zip_compression_level=6,
            quality=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )
        settings3 = VdscSettingsDTO(
            png_compression_level=5,
            zip_compression_level=6,
            quality=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

        assert settings1 == settings2
        assert settings1 != settings3

    def test_vdsc_settings_dto_access_nested_properties(self, quality_dto, schedule_rules_dto):
        """Testa acesso a propriedades aninhadas"""
        settings = VdscSettingsDTO(
            png_compression_level=3,
            zip_compression_level=6,
            quality=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

        assert settings.quality.high == 1080
        assert settings.schedule_event_rules.retry_backoff_factor == 2


@pytest.mark.unit
class TestS3ConfigDTO:
    """Testes para a classe S3ConfigDTO"""

    def test_create_s3_config_dto(self):
        """Testa criação de S3ConfigDTO com valores válidos"""
        s3_config = S3ConfigDTO(
            bucket_name="my-video-bucket",
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_processing="processing/"
        )

        assert s3_config.bucket_name == "my-video-bucket"
        assert s3_config.dir_uploads == "uploads/"
        assert s3_config.dir_finished == "finished/"
        assert s3_config.dir_processing == "processing/"

    def test_s3_config_dto_is_immutable(self):
        """Testa que S3ConfigDTO é imutável (frozen)"""
        s3_config = S3ConfigDTO(
            bucket_name="my-video-bucket",
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_processing="processing/"
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            s3_config.bucket_name = "other-bucket"

    def test_s3_config_dto_equality(self):
        """Testa comparação de igualdade entre instâncias"""
        s3_config1 = S3ConfigDTO(
            bucket_name="my-video-bucket",
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_processing="processing/"
        )
        s3_config2 = S3ConfigDTO(
            bucket_name="my-video-bucket",
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_processing="processing/"
        )
        s3_config3 = S3ConfigDTO(
            bucket_name="other-bucket",
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_processing="processing/"
        )

        assert s3_config1 == s3_config2
        assert s3_config1 != s3_config3

    def test_s3_config_dto_with_empty_strings(self):
        """Testa criação com strings vazias"""
        s3_config = S3ConfigDTO(
            bucket_name="",
            dir_uploads="",
            dir_finished="",
            dir_processing=""
        )

        assert s3_config.bucket_name == ""
        assert s3_config.dir_uploads == ""
        assert s3_config.dir_finished == ""
        assert s3_config.dir_processing == ""

    def test_s3_config_dto_without_trailing_slashes(self):
        """Testa criação sem barras no final dos diretórios"""
        s3_config = S3ConfigDTO(
            bucket_name="my-video-bucket",
            dir_uploads="uploads",
            dir_finished="finished",
            dir_processing="processing"
        )

        assert s3_config.dir_uploads == "uploads"
        assert s3_config.dir_finished == "finished"
        assert s3_config.dir_processing == "processing"


@pytest.mark.unit
class TestVdscConfigDTO:
    """Testes para a classe VdscConfigDTO"""

    @pytest.fixture
    def quality_dto(self):
        """Fixture com QualityDTO válido"""
        return QualityDTO(ultra=2160, high=1080, medium=720, low=480)

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
            png_compression_level=3,
            zip_compression_level=6,
            quality=quality_dto,
            schedule_event_rules=schedule_rules_dto
        )

    @pytest.fixture
    def s3_config_dto(self):
        """Fixture com S3ConfigDTO válido"""
        return S3ConfigDTO(
            bucket_name="my-video-bucket",
            dir_uploads="uploads/",
            dir_finished="finished/",
            dir_processing="processing/"
        )

    def test_create_vdsc_config_dto(self, s3_config_dto, vdsc_settings_dto):
        """Testa criação de VdscConfigDTO com valores válidos"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=s3_config_dto,
            vdsc=vdsc_settings_dto
        )

        assert config.aws_region == "us-east-1"
        assert config.dynamodb_table_name == "VideoSlice"
        assert config.event_bus_name == "video-slice-events"
        assert config.s3_bucket == s3_config_dto
        assert config.vdsc == vdsc_settings_dto

    def test_vdsc_config_dto_is_immutable(self, s3_config_dto, vdsc_settings_dto):
        """Testa que VdscConfigDTO é imutável (frozen)"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=s3_config_dto,
            vdsc=vdsc_settings_dto
        )

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.aws_region = "us-west-2"  # type: ignore

    def test_vdsc_config_dto_equality(self, s3_config_dto, vdsc_settings_dto):
        """Testa comparação de igualdade entre instâncias"""
        config1 = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=s3_config_dto,
            vdsc=vdsc_settings_dto
        )
        config2 = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=s3_config_dto,
            vdsc=vdsc_settings_dto
        )
        config3 = VdscConfigDTO(
            aws_region="us-west-2",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=s3_config_dto,
            vdsc=vdsc_settings_dto
        )

        assert config1 == config2
        assert config1 != config3

    def test_vdsc_config_dto_access_nested_properties(self, s3_config_dto, vdsc_settings_dto):
        """Testa acesso a propriedades profundamente aninhadas"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=s3_config_dto,
            vdsc=vdsc_settings_dto
        )

        assert config.s3_bucket.bucket_name == "my-video-bucket"
        assert config.s3_bucket.dir_uploads == "uploads/"
        assert config.vdsc.png_compression_level == 3
        assert config.vdsc.quality.high == 1080
        assert config.vdsc.schedule_event_rules.retry_backoff_factor == 2

    def test_vdsc_config_dto_with_different_regions(self, s3_config_dto, vdsc_settings_dto):
        """Testa criação com diferentes regiões AWS"""
        regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]

        for region in regions:
            config = VdscConfigDTO(
                aws_region=region,
                dynamodb_table_name="VideoSlice",
                event_bus_name="video-slice-events",
                s3_bucket=s3_config_dto,
                vdsc=vdsc_settings_dto
            )
            assert config.aws_region == region

    def test_vdsc_config_dto_complete_structure(self):
        """Testa criação completa de toda a hierarquia de DTOs"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=S3ConfigDTO(
                bucket_name="my-video-bucket",
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_processing="processing/"
            ),
            vdsc=VdscSettingsDTO(
                png_compression_level=3,
                zip_compression_level=6,
                quality=QualityDTO(
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
        assert config.dynamodb_table_name == "VideoSlice"
        assert config.event_bus_name == "video-slice-events"
        assert config.s3_bucket.bucket_name == "my-video-bucket"
        assert config.vdsc.png_compression_level == 3
        assert config.vdsc.quality.high == 1080
        assert config.vdsc.schedule_event_rules.retry_backoff_factor == 2

    def test_vdsc_config_dto_with_empty_strings(self, s3_config_dto, vdsc_settings_dto):
        """Testa criação com strings vazias"""
        config = VdscConfigDTO(
            aws_region="",
            dynamodb_table_name="",
            event_bus_name="",
            s3_bucket=s3_config_dto,
            vdsc=vdsc_settings_dto
        )

        assert config.aws_region == ""
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
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=S3ConfigDTO(
                bucket_name="vdsc-prd-s3-bucket",
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_processing="processing/"
            ),
            vdsc=VdscSettingsDTO(
                png_compression_level=3,
                zip_compression_level=6,
                quality=QualityDTO(ultra=2160, high=1080, medium=720, low=480),
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
        assert config.s3_bucket.bucket_name == "vdsc-prd-s3-bucket"
        assert config.s3_bucket.dir_uploads == "uploads/"
        assert config.vdsc.png_compression_level == 3
        assert config.vdsc.zip_compression_level == 6
        assert config.vdsc.quality.ultra == 2160
        assert config.vdsc.quality.high == 1080
        assert config.vdsc.quality.medium == 720
        assert config.vdsc.quality.low == 480
        assert config.vdsc.schedule_event_rules.retry_backoff_factor == 2
        assert "vdsc-retry" in config.vdsc.schedule_event_rules.retry_arn

    def test_config_immutability_at_all_levels(self):
        """Testa imutabilidade em todos os níveis da hierarquia"""
        config = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice",
            event_bus_name="video-slice-events",
            s3_bucket=S3ConfigDTO(
                bucket_name="my-bucket",
                dir_uploads="uploads/",
                dir_finished="finished/",
                dir_processing="processing/"
            ),
            vdsc=VdscSettingsDTO(
                png_compression_level=3,
                zip_compression_level=6,
                quality=QualityDTO(ultra=2160, high=1080, medium=720, low=480),
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
            config.s3_bucket.bucket_name = "other-bucket"  # type: ignore

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.vdsc.png_compression_level = 5  # type: ignore

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.vdsc.quality.high = 1920  # type: ignore

        with pytest.raises(AttributeError):
            # noinspection PyDataclass
            config.vdsc.schedule_event_rules.retry_backoff_factor = 3  # type: ignore

    def test_multiple_configs_independence(self):
        """Testa que múltiplas configurações são independentes"""
        config1 = VdscConfigDTO(
            aws_region="us-east-1",
            dynamodb_table_name="VideoSlice1",
            event_bus_name="events1",
            s3_bucket=S3ConfigDTO(
                bucket_name="bucket1",
                dir_uploads="uploads1/",
                dir_finished="finished1/",
                dir_processing="processing1/"
            ),
            vdsc=VdscSettingsDTO(
                png_compression_level=3,
                zip_compression_level=6,
                quality=QualityDTO(ultra=2160, high=1080, medium=720, low=480),
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
            dynamodb_table_name="VideoSlice2",
            event_bus_name="events2",
            s3_bucket=S3ConfigDTO(
                bucket_name="bucket2",
                dir_uploads="uploads2/",
                dir_finished="finished2/",
                dir_processing="processing2/"
            ),
            vdsc=VdscSettingsDTO(
                png_compression_level=5,
                zip_compression_level=9,
                quality=QualityDTO(ultra=1920, high=720, medium=480, low=360),
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
        assert config1.dynamodb_table_name != config2.dynamodb_table_name
        assert config1.s3_bucket.bucket_name != config2.s3_bucket.bucket_name
        assert config1.vdsc.png_compression_level != config2.vdsc.png_compression_level
        assert config1.vdsc.quality.high != config2.vdsc.quality.high
