import { Injectable } from '@angular/core';
import { HttpClient,HttpParams, HttpHeaders  } from '@angular/common/http';
import { Entradas} from './../entradas';

@Injectable({
  providedIn: 'root'
})
export class HttpService {

  constructor(
    private http:HttpClient
  ) {}
  /*
  httpHeader = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  } */

  buyPetition(variable: string){
    let splitted = variable.split(";",2)
    const params= new HttpParams().set("titulo",splitted[0]).set("tickets",splitted[1]);
    return this.http.get<Entradas>('http://localhost:5005/buy',{params});
  }
  recoverPetition(variable: string){
    const params= new HttpParams().set("ID",variable);
    
    return this.http.get<Entradas>('http://localhost:5005/recover',{params});
  }
}
