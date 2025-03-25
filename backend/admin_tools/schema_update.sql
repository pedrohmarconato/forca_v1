-- Script de atualização do esquema do banco de dados FORCA_V1
-- Este script atualiza o esquema existente e corrige problemas identificados

-- IMPORTANTE: Este script foi desenvolvido para corrigir discrepâncias entre
-- as definições de tabelas e o esquema real do banco de dados. Execute em partes
-- e verifique os resultados de cada seção antes de prosseguir.

----------------------------------------------
-- VERIFICAÇÃO DE TABELAS EXISTENTES
----------------------------------------------

-- Verifica a existência das tabelas principais e cria um relatório
DO $$
DECLARE
    tabela_nome TEXT;
    tabelas_dim TEXT[] := ARRAY[
        'dim_usuario', 'dim_objetivo', 'dim_restricao', 'dim_grupomuscular',
        'dim_exercicio', 'dim_modeloperiodizacao', 'dim_metodotreinamento',
        'dim_tiposessao', 'dim_variaveltreinamento', 'dim_humor', 'dim_tempodisponivel'
    ];
    tabelas_fato TEXT[] := ARRAY[
        'fato_treinamento', 'fato_ciclotreinamento', 'fato_microciclosemanal',
        'fato_sessaotreinamento', 'fato_sessaogrupomusuclar', 'fato_exerciciossessao',
        'fato_usuarioobjetivo', 'fato_usuariorestricao', 'fato_adaptacaotreinamento',
        'fato_aquecimentodesaquecimento', 'fato_exercicioaquecimento',
        'fato_progressaoexercicio', 'fato_substituicaoexercicio', 'fato_registrotreino',
        'fato_registroexercicio', 'fato_metricaprogresso'
    ];
    falta_tabela BOOLEAN := FALSE;
BEGIN
    RAISE NOTICE '=== VERIFICAÇÃO DE TABELAS EXISTENTES ===';
    
    -- Verificar tabelas de dimensão
    RAISE NOTICE 'Tabelas de dimensão:';
    FOREACH tabela_nome IN ARRAY tabelas_dim LOOP
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = tabela_nome) THEN
            RAISE NOTICE '  ✓ % - OK', tabela_nome;
        ELSE
            RAISE NOTICE '  ✗ % - NÃO EXISTE', tabela_nome;
            falta_tabela := TRUE;
        END IF;
    END LOOP;
    
    -- Verificar tabelas de fato
    RAISE NOTICE 'Tabelas de fato:';
    FOREACH tabela_nome IN ARRAY tabelas_fato LOOP
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = tabela_nome) THEN
            RAISE NOTICE '  ✓ % - OK', tabela_nome;
        ELSE
            RAISE NOTICE '  ✗ % - NÃO EXISTE', tabela_nome;
            falta_tabela := TRUE;
        END IF;
    END LOOP;
    
    -- Aviso final
    IF falta_tabela THEN
        RAISE NOTICE '';
        RAISE NOTICE 'AVISO: Algumas tabelas estão faltando no banco de dados.';
        RAISE NOTICE 'Execute o script create_indices.sql completo para criar as tabelas faltantes.';
    ELSE
        RAISE NOTICE '';
        RAISE NOTICE 'SUCESSO: Todas as tabelas existem no banco de dados.';
    END IF;
END $$;

----------------------------------------------
-- VERIFICAÇÃO E CORREÇÃO DA TABELA FATO_ADAPTACAOTREINAMENTO
----------------------------------------------

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== ATUALIZANDO A TABELA FATO_ADAPTACAOTREINAMENTO ===';
    
    -- Verificar se a tabela existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fato_adaptacaotreinamento') THEN
        RAISE NOTICE 'A tabela fato_adaptacaotreinamento não existe. Execute o script create_indices.sql primeiro.';
        RETURN;
    END IF;
    
    -- Lista de colunas esperadas
    DECLARE
        colunas_esperadas TEXT[] := ARRAY[
            'adaptacao_id', 'usuario_id', 'treinamento_id', 'sessao_original_id',
            'humor_id', 'tempo_disponivel_id', 'tipo', 'nivel', 'data_criacao',
            'ajustes_aplicados', 'status', 'created_at', 'updated_at'
        ];
        coluna TEXT;
    BEGIN
        RAISE NOTICE 'Verificação de colunas:';
        
        -- Verificar cada coluna esperada
        FOREACH coluna IN ARRAY colunas_esperadas LOOP
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'fato_adaptacaotreinamento' 
                AND column_name = coluna
            ) THEN
                RAISE NOTICE '  ✓ % - OK', coluna;
            ELSE
                RAISE NOTICE '  ✗ % - FALTANDO (Será adicionada)', coluna;
                
                -- Adicionar a coluna faltante com o tipo apropriado
                IF coluna = 'adaptacao_id' THEN
                    EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD COLUMN ' || coluna || ' UUID PRIMARY KEY';
                ELSIF coluna LIKE '%_id' THEN
                    EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD COLUMN ' || coluna || ' UUID';
                ELSIF coluna = 'ajustes_aplicados' THEN
                    EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD COLUMN ' || coluna || ' JSONB';
                ELSIF coluna IN ('created_at', 'updated_at', 'data_criacao') THEN
                    EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD COLUMN ' || coluna || ' TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP';
                ELSE
                    EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD COLUMN ' || coluna || ' TEXT';
                END IF;
                
                RAISE NOTICE '    Coluna % adicionada', coluna;
            END IF;
        END LOOP;
    END;
END $$;

----------------------------------------------
-- VERIFICAÇÃO DA TABELA FATO_SESSAOTREINAMENTO
----------------------------------------------

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== VERIFICANDO A TABELA FATO_SESSAOTREINAMENTO ===';
    
    -- Verificar se a tabela existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fato_sessaotreinamento') THEN
        RAISE NOTICE 'A tabela fato_sessaotreinamento não existe. Execute o script create_indices.sql primeiro.';
        RETURN;
    END IF;
    
    -- Verificar a coluna tipo_sessao_id
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'fato_sessaotreinamento' 
        AND column_name = 'tipo_sessao_id'
    ) THEN
        RAISE NOTICE '  ✓ tipo_sessao_id - OK';
    ELSE
        RAISE NOTICE '  ✗ tipo_sessao_id - FALTANDO (Será adicionada)';
        EXECUTE 'ALTER TABLE fato_sessaotreinamento ADD COLUMN tipo_sessao_id UUID';
        RAISE NOTICE '    Coluna tipo_sessao_id adicionada';
    END IF;
END $$;

----------------------------------------------
-- RECRIAÇÃO DE ÍNDICES COM TRATAMENTO DE ERROS
----------------------------------------------

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== RECRIANDO ÍNDICES PARA FATO_ADAPTACAOTREINAMENTO ===';
    
    -- Verificar se a tabela existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fato_adaptacaotreinamento') THEN
        RAISE NOTICE 'A tabela fato_adaptacaotreinamento não existe. Execute o script create_indices.sql primeiro.';
        RETURN;
    END IF;
    
    -- Lista de índices para recriar
    DECLARE
        indices TEXT[] := ARRAY[
            'idx_fato_adaptacaotreinamento_sessao_original:sessao_original_id',
            'idx_fato_adaptacaotreinamento_tipo:tipo',
            'idx_fato_adaptacaotreinamento_nivel:nivel',
            'idx_fato_adaptacaotreinamento_usuario:usuario_id',
            'idx_fato_adaptacaotreinamento_treinamento:treinamento_id',
            'idx_fato_adaptacaotreinamento_data_criacao:created_at'
        ];
        item TEXT;
        indice_info TEXT[];
        indice_nome TEXT;
        indice_coluna TEXT;
    BEGIN
        -- Para cada índice na lista
        FOREACH item IN ARRAY indices LOOP
            -- Separar nome do índice e coluna
            indice_info := string_to_array(item, ':');
            indice_nome := indice_info[1];
            indice_coluna := indice_info[2];
            
            -- Remover índice se existir
            EXECUTE 'DROP INDEX IF EXISTS ' || indice_nome;
            
            -- Verificar se a coluna existe
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'fato_adaptacaotreinamento' 
                AND column_name = indice_coluna
            ) THEN
                -- Criar índice
                BEGIN
                    EXECUTE 'CREATE INDEX ' || indice_nome || ' ON fato_adaptacaotreinamento (' || indice_coluna || ')';
                    RAISE NOTICE '  ✓ Índice % criado com sucesso', indice_nome;
                EXCEPTION
                    WHEN OTHERS THEN
                        RAISE NOTICE '  ✗ Erro ao criar índice %: %', indice_nome, SQLERRM;
                END;
            ELSE
                RAISE NOTICE '  ✗ Não foi possível criar índice %: coluna % não existe', indice_nome, indice_coluna;
            END IF;
        END LOOP;
        
        -- Índices compostos
        BEGIN
            EXECUTE 'DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_tipo_nivel';
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'fato_adaptacaotreinamento' 
                AND column_name = 'tipo'
            ) AND EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'fato_adaptacaotreinamento' 
                AND column_name = 'nivel'
            ) THEN
                EXECUTE 'CREATE INDEX idx_fato_adaptacaotreinamento_tipo_nivel ON fato_adaptacaotreinamento (tipo, nivel)';
                RAISE NOTICE '  ✓ Índice idx_fato_adaptacaotreinamento_tipo_nivel criado com sucesso';
            ELSE
                RAISE NOTICE '  ✗ Não foi possível criar índice composto: colunas tipo ou nivel não existem';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE '  ✗ Erro ao criar índice tipo_nivel: %', SQLERRM;
        END;
        
        BEGIN
            EXECUTE 'DROP INDEX IF EXISTS idx_fato_adaptacaotreinamento_usuario_sessao';
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'fato_adaptacaotreinamento' 
                AND column_name = 'usuario_id'
            ) AND EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'fato_adaptacaotreinamento' 
                AND column_name = 'sessao_original_id'
            ) THEN
                EXECUTE 'CREATE INDEX idx_fato_adaptacaotreinamento_usuario_sessao ON fato_adaptacaotreinamento (usuario_id, sessao_original_id)';
                RAISE NOTICE '  ✓ Índice idx_fato_adaptacaotreinamento_usuario_sessao criado com sucesso';
            ELSE
                RAISE NOTICE '  ✗ Não foi possível criar índice composto: colunas usuario_id ou sessao_original_id não existem';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE '  ✗ Erro ao criar índice usuario_sessao: %', SQLERRM;
        END;
    END;
END $$;

----------------------------------------------
-- CRIAÇÃO DE CHAVES ESTRANGEIRAS
----------------------------------------------

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== TENTATIVA DE CRIAÇÃO DE CHAVES ESTRANGEIRAS ===';
    RAISE NOTICE 'NOTA: Esta operação pode falhar no Supabase SQL Editor. Em caso de erros, execute os comandos manualmente no psql ou via API Supabase.';
    
    -- Verificar se as tabelas dependentes existem
    DECLARE
        dependencias TEXT[] := ARRAY[
            'dim_usuario:usuario_id', 
            'fato_treinamento:treinamento_id',
            'fato_sessaotreinamento:sessao_id',
            'dim_humor:humor_id',
            'dim_tempodisponivel:tempo_disponivel_id'
        ];
        item TEXT;
        tabela_info TEXT[];
        tabela_dependente TEXT;
        coluna_dependente TEXT;
        pode_criar_fks BOOLEAN := TRUE;
    BEGIN
        -- Verificar se cada tabela de referência existe
        FOREACH item IN ARRAY dependencias LOOP
            tabela_info := string_to_array(item, ':');
            tabela_dependente := tabela_info[1];
            coluna_dependente := tabela_info[2];
            
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = tabela_dependente) THEN
                RAISE NOTICE '  ✓ Tabela % existe', tabela_dependente;
            ELSE
                RAISE NOTICE '  ✗ Tabela % não existe - Não será possível criar chaves estrangeiras', tabela_dependente;
                pode_criar_fks := FALSE;
            END IF;
        END LOOP;
        
        -- Se todas as tabelas dependentes existem, tentar criar as FKs
        IF pode_criar_fks THEN
            RAISE NOTICE 'Tentando criar chaves estrangeiras...';
            
            -- Adicionar FK para usuario_id
            BEGIN
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento DROP CONSTRAINT IF EXISTS fk_fato_adaptacao_usuario';
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD CONSTRAINT fk_fato_adaptacao_usuario FOREIGN KEY (usuario_id) REFERENCES dim_usuario(usuario_id)';
                RAISE NOTICE '  ✓ FK fk_fato_adaptacao_usuario criada com sucesso';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE '  ✗ Erro ao criar FK para usuario_id: %', SQLERRM;
            END;
            
            -- Adicionar FK para treinamento_id
            BEGIN
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento DROP CONSTRAINT IF EXISTS fk_fato_adaptacao_treinamento';
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD CONSTRAINT fk_fato_adaptacao_treinamento FOREIGN KEY (treinamento_id) REFERENCES fato_treinamento(treinamento_id)';
                RAISE NOTICE '  ✓ FK fk_fato_adaptacao_treinamento criada com sucesso';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE '  ✗ Erro ao criar FK para treinamento_id: %', SQLERRM;
            END;
            
            -- Adicionar FK para sessao_original_id
            BEGIN
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento DROP CONSTRAINT IF EXISTS fk_fato_adaptacao_sessao';
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD CONSTRAINT fk_fato_adaptacao_sessao FOREIGN KEY (sessao_original_id) REFERENCES fato_sessaotreinamento(sessao_id)';
                RAISE NOTICE '  ✓ FK fk_fato_adaptacao_sessao criada com sucesso';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE '  ✗ Erro ao criar FK para sessao_original_id: %', SQLERRM;
            END;
            
            -- Adicionar FK para humor_id
            BEGIN
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento DROP CONSTRAINT IF EXISTS fk_fato_adaptacao_humor';
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD CONSTRAINT fk_fato_adaptacao_humor FOREIGN KEY (humor_id) REFERENCES dim_humor(humor_id)';
                RAISE NOTICE '  ✓ FK fk_fato_adaptacao_humor criada com sucesso';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE '  ✗ Erro ao criar FK para humor_id: %', SQLERRM;
            END;
            
            -- Adicionar FK para tempo_disponivel_id
            BEGIN
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento DROP CONSTRAINT IF EXISTS fk_fato_adaptacao_tempo';
                EXECUTE 'ALTER TABLE fato_adaptacaotreinamento ADD CONSTRAINT fk_fato_adaptacao_tempo FOREIGN KEY (tempo_disponivel_id) REFERENCES dim_tempodisponivel(tempo_disponivel_id)';
                RAISE NOTICE '  ✓ FK fk_fato_adaptacao_tempo criada com sucesso';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE '  ✗ Erro ao criar FK para tempo_disponivel_id: %', SQLERRM;
            END;
        ELSE
            RAISE NOTICE 'Não é possível criar chaves estrangeiras devido à falta de tabelas dependentes.';
        END IF;
    END;
END $$;

----------------------------------------------
-- VERIFICAÇÃO FINAL
----------------------------------------------

DO $$
DECLARE
    coluna RECORD;
    indice RECORD;
    fk RECORD;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== VERIFICAÇÃO FINAL DA TABELA FATO_ADAPTACAOTREINAMENTO ===';
    
    -- Verificar se a tabela existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fato_adaptacaotreinamento') THEN
        RAISE NOTICE 'A tabela fato_adaptacaotreinamento não existe.';
        RETURN;
    END IF;
    
    -- Listar todas as colunas
    RAISE NOTICE 'Colunas:';
    FOR coluna IN 
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'fato_adaptacaotreinamento'
        ORDER BY ordinal_position
    LOOP
        RAISE NOTICE '  %: %', coluna.column_name, coluna.data_type;
    END LOOP;
    
    -- Listar todos os índices
    RAISE NOTICE '';
    RAISE NOTICE 'Índices:';
    FOR indice IN 
        SELECT indexname, indexdef
        FROM pg_indexes 
        WHERE tablename = 'fato_adaptacaotreinamento'
        ORDER BY indexname
    LOOP
        RAISE NOTICE '  %: %', indice.indexname, indice.indexdef;
    END LOOP;
    
    -- Listar todas as chaves estrangeiras
    RAISE NOTICE '';
    RAISE NOTICE 'Chaves Estrangeiras:';
    FOR fk IN
        SELECT
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS references_table,
            ccu.column_name AS references_column
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name = 'fato_adaptacaotreinamento'
    LOOP
        RAISE NOTICE '  %: % → %.%', fk.constraint_name, fk.column_name, fk.references_table, fk.references_column;
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '=== FIM DA ATUALIZAÇÃO DO ESQUEMA ===';
    RAISE NOTICE '';
    RAISE NOTICE 'Para verificar novamente o esquema após as atualizações, execute:';
    RAISE NOTICE 'SELECT column_name, data_type FROM information_schema.columns WHERE table_name = ''fato_adaptacaotreinamento'' ORDER BY ordinal_position;';
    RAISE NOTICE '';
END $$;