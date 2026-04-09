-- 添加缺失的数据库字段
-- 在SQL Server Management Studio中执行此脚本

USE [baojia];  -- 替换为你的数据库名
GO

-- 1. cabinets表添加新字段
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'cabinets' AND COLUMN_NAME = 'control_category')
BEGIN
    ALTER TABLE cabinets ADD control_category NVARCHAR(50) NULL;
    PRINT 'Added control_category to cabinets';
END
ELSE
    PRINT 'control_category already exists in cabinets';

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'cabinets' AND COLUMN_NAME = 'cabinet_type')
BEGIN
    ALTER TABLE cabinets ADD cabinet_type NVARCHAR(100) NULL;
    PRINT 'Added cabinet_type to cabinets';
END
ELSE
    PRINT 'cabinet_type already exists in cabinets';

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'cabinets' AND COLUMN_NAME = 'control_structure')
BEGIN
    ALTER TABLE cabinets ADD control_structure NVARCHAR(100) NULL;
    PRINT 'Added control_structure to cabinets';
END
ELSE
    PRINT 'control_structure already exists in cabinets';

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'cabinets' AND COLUMN_NAME = 'quotation_mode')
BEGIN
    ALTER TABLE cabinets ADD quotation_mode NVARCHAR(50) NULL;
    PRINT 'Added quotation_mode to cabinets';
END
ELSE
    PRINT 'quotation_mode already exists in cabinets';

-- 2. structure_components表添加新字段
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'structure_components' AND COLUMN_NAME = 'circuit_type')
BEGIN
    ALTER TABLE structure_components ADD circuit_type NVARCHAR(100) NULL;
    PRINT 'Added circuit_type to structure_components';
END
ELSE
    PRINT 'circuit_type already exists in structure_components';

-- 3. base_components表添加新字段
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'base_components' AND COLUMN_NAME = 'component_category')
BEGIN
    ALTER TABLE base_components ADD component_category NVARCHAR(100) NULL;
    PRINT 'Added component_category to base_components';
END
ELSE
    PRINT 'component_category already exists in base_components';

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'base_components' AND COLUMN_NAME = 'is_auto_matched')
BEGIN
    ALTER TABLE base_components ADD is_auto_matched BIT NOT NULL DEFAULT 0;
    PRINT 'Added is_auto_matched to base_components';
END
ELSE
    PRINT 'is_auto_matched already exists in base_components';

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'base_components' AND COLUMN_NAME = 'is_hidden')
BEGIN
    ALTER TABLE base_components ADD is_hidden BIT NOT NULL DEFAULT 0;
    PRINT 'Added is_hidden to base_components';
END
ELSE
    PRINT 'is_hidden already exists in base_components';

GO

PRINT '';
PRINT '============================================================';
PRINT '数据库迁移完成！';
PRINT '============================================================';
