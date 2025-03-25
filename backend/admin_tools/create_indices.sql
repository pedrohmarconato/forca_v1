-- Script de criação e atualização do banco de dados FORCA_V1
-- Este script corrige as tabelas, adiciona colunas faltantes e cria índices

-- IMPORTANTE: O Supabase tem algumas limitações com chaves estrangeiras quando
-- executado via SQL Editor. Se você encontrar problemas, talvez seja necessário
-- executar este script por partes ou aplicar manualmente algumas das alterações
-- através da interface do Supabase.

----------------------------------------------
-- CORREÇÃO DA TABELA FATO_ADAPTACAOTREINAMENTO
----------------------------------------------

-- Verificar se a coluna usuario_id existe na tabela fato_adaptacaotreinamento
DO $$
BEGIN
    -- Tentar adicionar a coluna usuario_id se ela não existir
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'fato_adaptacaotreinamento' 
        AND column_name = 'usuario_id'
    ) THEN
        -- Adicionar a coluna usuario_id que está faltando
        ALTER TABLE fato_adaptacaotreinamento ADD COLUMN usuario_id UUID;
        
        -- Registrar alteração no log
        RAISE NOTICE 'Coluna usuario_id adicionada à tabela fato_adaptacaotreinamento';
    ELSE
        RAISE NOTICE 'Coluna usuario_id já existe na tabela fato_adaptacaotreinamento';
    END IF;
    
    -- Verificar se a coluna treinamento_id existe
    -- (conforme documento original, esta coluna também deveria existir)
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'fato_adaptacaotreinamento' 
        AND column_name = 'treinamento_id'
    ) THEN
        -- Adicionar a coluna treinamento_id que pode estar faltando
        ALTER TABLE fato_adaptacaotreinamento ADD COLUMN treinamento_id UUID;
        
        RAISE NOTICE 'Coluna treinamento_id adicionada à tabela fato_adaptacaotreinamento';
    ELSE
        RAISE NOTICE 'Coluna treinamento_id já existe na tabela fato_adaptacaotreinamento';
    END IF;
    
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE 'A tabela fato_adaptacaotreinamento não existe. Será criada pelo script.';
END $$;

-- Recria a tabela fato_adaptacaotreinamento apenas se ela não existir
CREATE TABLE IF NOT EXISTS fato_adaptacaotreinamento (
    adaptacao_id UUID PRIMARY KEY,
    usuario_id UUID,                         -- Adicionado conforme necessidade
    treinamento_id UUID,                     -- Conforme documento original
    sessao_original_id UUID,
    humor_id UUID,
    tempo_disponivel_id UUID,
    tipo TEXT,
    nivel TEXT,
    data_criacao TIMESTAMP WITH TIME ZONE,
    ajustes_aplicados JSONB,
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comentamos as constraints devido a erros prévios
-- Elas podem ser adicionadas manualmente depois que a estrutura estiver correta
-- ALTER TABLE fato_adaptacaotreinamento 
--     ADD CONSTRAINT fk_fato_adaptacao_usuario 
--     FOREIGN KEY (usuario_id) REFERENCES dim_usuario(usuario_id);
--
-- ALTER TABLE fato_adaptacaotreinamento 
--     ADD CONSTRAINT fk_fato_adaptacao_treinamento 
--     FOREIGN KEY (treinamento_id) REFERENCES fato_treinamento(treinamento_id);
--
-- ALTER TABLE fato_adaptacaotreinamento 
--     ADD CONSTRAINT fk_fato_adaptacao_sessao 
--     FOREIGN KEY (sessao_original_id) REFERENCES fato_sessaotreinamento(sessao_id);
--
-- ALTER TABLE fato_adaptacaotreinamento 
--     ADD CONSTRAINT fk_fato_adaptacao_humor 
--     FOREIGN KEY (humor_id) REFERENCES dim_humor(humor_id);
--
-- ALTER TABLE fato_adaptacaotreinamento 
--     ADD CONSTRAINT fk_fato_adaptacao_tempo 
--     FOREIGN KEY (tempo_disponivel_id) REFERENCES dim_tempodisponivel(tempo_disponivel_id);

----------------------------------------------
-- ÍNDICES PARA TABELA FATO_ADAPTACAOTREINAMENTO
----------------------------------------------

-- Primeiro remover os índices existentes para evitar erros de duplicação
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_sessao_original;
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_tipo;
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_nivel;
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_usuario;
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_treinamento;
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_data_criacao;
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_tipo_nivel;
DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_usuario_sessao;

-- Criar índices com tratamento de erro para cada um
DO $$
BEGIN
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_sessao_original ON fato_adaptacaotreinamento (sessao_original_id);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_sessao_original criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_sessao_original já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Coluna sessao_original_id não encontrada na tabela fato_adaptacaotreinamento';
    END;
    
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_tipo ON fato_adaptacaotreinamento (tipo);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_tipo criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_tipo já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Coluna tipo não encontrada na tabela fato_adaptacaotreinamento';
    END;
    
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_nivel ON fato_adaptacaotreinamento (nivel);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_nivel criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_nivel já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Coluna nivel não encontrada na tabela fato_adaptacaotreinamento';
    END;
    
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_usuario ON fato_adaptacaotreinamento (usuario_id);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_usuario criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_usuario já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Coluna usuario_id não encontrada na tabela fato_adaptacaotreinamento';
    END;
    
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_treinamento ON fato_adaptacaotreinamento (treinamento_id);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_treinamento criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_treinamento já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Coluna treinamento_id não encontrada na tabela fato_adaptacaotreinamento';
    END;
    
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_data_criacao ON fato_adaptacaotreinamento (created_at);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_data_criacao criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_data_criacao já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Coluna created_at não encontrada na tabela fato_adaptacaotreinamento';
    END;
    
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_tipo_nivel ON fato_adaptacaotreinamento (tipo, nivel);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_tipo_nivel criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_tipo_nivel já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Colunas tipo ou nivel não encontradas na tabela fato_adaptacaotreinamento';
    END;
    
    BEGIN
        CREATE INDEX idx_fato_adaptacaotreinamento_usuario_sessao ON fato_adaptacaotreinamento (usuario_id, sessao_original_id);
        RAISE NOTICE 'Índice idx_fato_adaptacaotreinamento_usuario_sessao criado com sucesso';
    EXCEPTION
        WHEN duplicate_table THEN 
            RAISE NOTICE 'O índice idx_fato_adaptacaotreinamento_usuario_sessao já existe';
        WHEN undefined_column THEN
            RAISE WARNING 'Colunas usuario_id ou sessao_original_id não encontradas na tabela fato_adaptacaotreinamento';
    END;
END $$;

-- Verificar e exibir as colunas existentes na tabela
DO $$
DECLARE
    coluna RECORD;
BEGIN
    RAISE NOTICE 'Colunas existentes na tabela fato_adaptacaotreinamento:';
    FOR coluna IN 
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'fato_adaptacaotreinamento'
        ORDER BY ordinal_position
    LOOP
        RAISE NOTICE '%: %', coluna.column_name, coluna.data_type;
    END LOOP;
END $$;

-- Verificação final de índices
DO $$
DECLARE
    indice RECORD;
BEGIN
    RAISE NOTICE 'Índices existentes na tabela fato_adaptacaotreinamento:';
    FOR indice IN 
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'fato_adaptacaotreinamento'
        ORDER BY indexname
    LOOP
        RAISE NOTICE '%', indice.indexname;
    END LOOP;
END $$;

-- Dica para o usuário
DO $$
BEGIN
    RAISE NOTICE '------------------------------------------------------------';
    RAISE NOTICE 'Instruções para verificar e resolver problemas:';
    RAISE NOTICE '1. Se houve erros de "coluna não encontrada", execute a consulta:';
    RAISE NOTICE 'SELECT column_name, data_type FROM information_schema.columns WHERE table_name = ''fato_adaptacaotreinamento'';';
    RAISE NOTICE '2. Para corrigir manualmente uma coluna faltante, execute:';
    RAISE NOTICE 'ALTER TABLE fato_adaptacaotreinamento ADD COLUMN nome_coluna TIPO_DADOS;';
    RAISE NOTICE '3. Para criar os índices em cada coluna, execute:';
    RAISE NOTICE 'CREATE INDEX idx_fato_adaptacaotreinamento_NOME_COLUNA ON fato_adaptacaotreinamento (NOME_COLUNA);';
    RAISE NOTICE '------------------------------------------------------------';
END $$;