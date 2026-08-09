export type TipoUsuario = 'admin' | 'cliente' | 'usuario';

export interface User {
  id: number;
  username: string;
  email: string;
  tipo_usuario: TipoUsuario;

  // 🔹 datos de perfil del cliente
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  provincia?: string;
  codigo_postal?: string;
}