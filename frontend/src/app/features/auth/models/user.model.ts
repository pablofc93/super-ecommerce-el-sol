export type TipoUsuario = 'admin' | 'cliente' | 'usuario';

//la interfaz User representa la información de un usuario autenticado
export interface User {
  id: number;
  username: string;
  email: string;
  tipo_usuario: TipoUsuario;

  // 🔹 datos de perfil del cliente
  // ? indica que los campos son opcionales
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  provincia?: string;
  codigo_postal?: string;
}