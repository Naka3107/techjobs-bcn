export interface Oferta {
  id: number;
  empresa_id: number;
  nombre_empresa: string;
  puesto: string;
  salario: number;
  pais: string;
  ciudad: string;
  tecnologias: string[];
}