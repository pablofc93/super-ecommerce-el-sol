export interface UsuarioAdmin {
  id: number;
  username: string;
  email: string;
  tipo_usuario: 'admin' | 'cliente';
}