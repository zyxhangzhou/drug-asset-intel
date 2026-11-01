## ADDED Requirements

### Requirement: Optional access password
应用 SHALL 支持通过环境变量配置一个访问密码。配置了密码时，除健康检查接口外的所有请求（前端页面、静态文件、API）SHALL 要求 HTTP 基本认证，密码不符时返回 HTTP 401 并提示浏览器弹出登录框；用户名不做限制。未配置密码时 SHALL 不要求认证，行为与之前相同。密码 SHALL 只来自环境变量，不写入仓库。

#### Scenario: Password not configured
- **WHEN** 未配置访问密码，请求候选名单接口
- **THEN** 返回 HTTP 200

#### Scenario: Request without credentials
- **WHEN** 已配置访问密码，请求前端首页或任一 API 时不带认证信息
- **THEN** 返回 HTTP 401，响应头要求基本认证

#### Scenario: Correct password
- **WHEN** 已配置访问密码，请求带正确密码的基本认证
- **THEN** 正常返回页面或数据

#### Scenario: Health check stays open
- **WHEN** 已配置访问密码，部署平台不带认证请求健康检查接口
- **THEN** 返回 HTTP 200
