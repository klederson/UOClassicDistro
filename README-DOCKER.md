# POL Server Docker Setup com Interface Web

Este projeto fornece uma configuração completa do servidor POL (Penultima Online) em containers Docker com uma interface web moderna para gerenciamento.

## Funcionalidades

### Interface Web
- **Dashboard**: Visão geral do status do servidor, uso de recursos e estatísticas
- **Gerenciamento de Contas**: Criar, editar, excluir e gerenciar contas de jogadores
- **Controle do Servidor**: Iniciar, parar e reiniciar o servidor
- **Visualização de Logs**: Ver logs em tempo real e histórico
- **Configuração**: Editar configurações do servidor através da interface

### API Backend
- API RESTful completa para todas as operações
- Autenticação JWT para segurança
- WebSocket para logs em tempo real
- Monitoramento de recursos do sistema

### Infraestrutura Docker
- Containers separados para cada serviço
- Docker Compose para orquestração
- Nginx como reverse proxy
- SSL/TLS habilitado
- Volumes persistentes para dados

## Pré-requisitos

- Docker e Docker Compose instalados
- Arquivos do cliente UO na pasta `MUL/`
- Pelo menos 2GB de RAM disponível

## Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd <diretorio-do-projeto>
```

### 2. Configure os arquivos do UO
Coloque os arquivos do cliente UO na pasta `MUL/`:
```bash
mkdir -p MUL
# Copie os arquivos .mul e .idx para esta pasta
```

### 3. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
POL_ADMIN_PASSWORD=sua_senha_admin
API_SECRET_KEY=sua_chave_secreta_aqui
POL_SERVER_NAME=Meu_Servidor_POL
```

### 4. Gere o certificado SSL (para desenvolvimento)
```bash
chmod +x nginx/ssl/generate-cert.sh
./nginx/ssl/generate-cert.sh
```

### 5. Construa e inicie os containers
```bash
docker-compose up -d --build
```

## Acessando a Interface

Após iniciar os containers, acesse:

- **Interface Web**: http://localhost ou https://localhost:443
- **API**: http://localhost:8001
- **Servidor POL**: porta 5003

### Login Padrão
- **Usuário**: admin
- **Senha**: (definida no arquivo .env como POL_ADMIN_PASSWORD)

## Estrutura dos Containers

### pol-server
- Container principal do servidor POL
- Executa o servidor de jogo
- Volumes montados para dados persistentes

### pol-api
- API backend em FastAPI
- Gerencia todas as operações do servidor
- Conecta-se ao container do servidor via Docker API

### pol-web
- Interface web em Vue.js
- Dashboard responsivo e moderno
- Comunicação em tempo real via WebSocket

### pol-nginx
- Reverse proxy e balanceador de carga
- Termina SSL/TLS
- Roteia requisições para os serviços apropriados

## Comandos Úteis

### Ver logs dos containers
```bash
# Todos os containers
docker-compose logs -f

# Container específico
docker-compose logs -f pol-server
```

### Parar todos os serviços
```bash
docker-compose down
```

### Reiniciar um serviço específico
```bash
docker-compose restart pol-api
```

### Executar comandos no container do servidor
```bash
docker-compose exec pol-server bash
```

### Fazer backup dos dados
```bash
docker-compose exec pol-server tar -czf /tmp/backup.tar.gz /workspace/data /workspace/accounts
docker cp pol-server:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

## Configuração Avançada

### Mudando Portas
Edite o `docker-compose.yml` para alterar as portas expostas:
```yaml
services:
  pol-server:
    ports:
      - "5003:5003"  # Altere a porta externa aqui
```

### Aumentando Limites de Recursos
No `docker-compose.yml`, adicione limites de recursos:
```yaml
services:
  pol-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Habilitando Modo de Produção
1. Use certificados SSL válidos em vez de auto-assinados
2. Configure um domínio real no nginx
3. Desabilite o modo debug na API
4. Use senhas fortes e únicas
5. Configure backups automáticos

## Troubleshooting

### Container não inicia
```bash
# Verifique os logs
docker-compose logs pol-server

# Verifique se as portas estão disponíveis
netstat -tulpn | grep -E '(5003|80|443|8001)'
```

### Erro de permissão
```bash
# Ajuste as permissões
sudo chown -R 1000:1000 ./data ./accounts ./logs
```

### API não conecta ao servidor
Verifique se o Docker socket está montado corretamente:
```bash
docker-compose exec pol-api ls -la /var/run/docker.sock
```

## Segurança

### Recomendações para Produção
1. **Mude todas as senhas padrão**
2. **Use HTTPS com certificados válidos**
3. **Configure firewall para limitar acesso**
4. **Mantenha os containers atualizados**
5. **Implemente backup regular**
6. **Monitor logs de segurança**

### Firewall (ufw)
```bash
# Permitir apenas portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5003/tcp
sudo ufw enable
```

## Manutenção

### Atualizando o servidor POL
1. Faça backup dos dados
2. Pare os containers: `docker-compose down`
3. Atualize os arquivos do POL
4. Reconstrua: `docker-compose up -d --build`

### Limpeza de logs
```bash
# Limpar logs antigos
docker-compose exec pol-server find /workspace/logs -name "*.log" -mtime +30 -delete
```

### Monitoramento
A interface web fornece monitoramento em tempo real, mas você também pode usar:
```bash
# Ver uso de recursos
docker stats

# Monitorar logs
docker-compose logs -f --tail=100
```

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs dos containers
2. Consulte a documentação do POL
3. Abra uma issue no repositório

## Licença

Este projeto segue a mesma licença do POL Server.