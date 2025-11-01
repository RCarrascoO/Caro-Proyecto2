program pas_client_send_data;
{
  Stub en Lazarus/FreePascal para leer `data.dat` con la estructura indicada
  por la consigna y realizar:
    1) POST JSON -> /upload-json (application/json)
    2) POST stream raw -> /upload-stream (application/octet-stream)

  Requisitos en Lazarus: paquete Indy (TIdHTTP) instalado. Añadir IdHTTP en Uses.
}

uses
  Classes, SysUtils, DateUtils, IdHTTP, IdSSLOpenSSL; // IdSSLOpenSSL opcional si HTTPS

type
  TRegistro = packed record
    id: Byte;
    te: Byte;
    hr: Byte;
    mp01: Word;
    mp25: Word;
    mp10: Word;
    h01: Word;
    h25: Word;
    h50: Word;
    h10: Word;
  end;

const
  RECORD_SIZE = SizeOf(TRegistro);

function ReadLastRecords(const AFile: string; Count: Integer): TArray<TRegistro>;
var
  fs: TFileStream;
  totalRecords, toRead, i: Integer;
  buf: TRegistro;
  resList: TList;
begin
  resList := TList.Create;
  try
    if not FileExists(AFile) then
      Exit(nil);
    fs := TFileStream.Create(AFile, fmOpenRead or fmShareDenyNone);
    try
      totalRecords := fs.Size div RECORD_SIZE;
      if totalRecords = 0 then
        Exit(nil);
      if Count > totalRecords then
        toRead := totalRecords
      else
        toRead := Count;
      // Seek to start of the block we want to read
      fs.Position := (totalRecords - toRead) * RECORD_SIZE;
      for i := 0 to toRead - 1 do
      begin
        fs.ReadBuffer(buf, RECORD_SIZE);
        resList.Add(Pointer(PtrInt(Pointer(@buf)))) ; // temporary, we will copy
        // Instead of adding pointer to local buf, we create a new copy
        // We'll handle properly after loop
      end;
      // Rewind and reread properly into dynamic array
      fs.Position := (totalRecords - toRead) * RECORD_SIZE;
      SetLength(Result, toRead);
      for i := 0 to toRead - 1 do
      begin
        fs.ReadBuffer(Result[i], RECORD_SIZE);
      end;
    finally
      fs.Free;
    end;
  finally
    resList.Free;
  end;
end;

function UnixNow: Int64;
begin
  Result := DateTimeToUnix(Now);
end;

function GetFileSize(const AFile: string): Int64;
var
  fs: TFileStream;
begin
  Result := 0;
  if FileExists(AFile) then
  begin
    fs := TFileStream.Create(AFile, fmOpenRead or fmShareDenyNone);
    try
      Result := fs.Size;
    finally
      fs.Free;
    end;
  end;
end;

function BuildJSONPayload(const regs: TArray<TRegistro>): string;
var
  i: Integer;
  sb: TStringList;
  tsBase: Int64;
  n: Integer;
  clientId: string;
begin
  sb := TStringList.Create;
  try
    n := Length(regs);
    if n = 0 then
      Exit('{}');
    tsBase := UnixNow;
    clientId := 'client' + IntToStr(regs[n-1].id);
    sb.Add('{');
    sb.Add(Format('  "client_id": "%s",', [clientId]));
    sb.Add('  "samples": [');
    for i := 0 to n - 1 do
    begin
      // timestamp: spread over last n minutes
      sb.Add(Format('    {"ts": %d, "mp01": %d, "mp25": %d, "mp10": %d, "temp": %d, "hr": %d}%s',
        [tsBase - (n - 1 - i) * 60,
         regs[i].mp01,
         regs[i].mp25,
         regs[i].mp10,
         regs[i].te,
         regs[i].hr,
         IfThen(i = n - 1, '', ',')]));
    end;
    sb.Add('  ]');
    sb.Add('}');
    Result := sb.Text;
  finally
    sb.Free;
  end;
end;

procedure PostJSON(const URL: string; const JSONPayload: string);
var
  http: TIdHTTP;
  ss: TStringStream;
  resp: string;
begin
  http := TIdHTTP.Create(nil);
  ss := TStringStream.Create(JSONPayload, TEncoding.UTF8);
  try
    http.Request.ContentType := 'application/json';
    resp := http.Post(URL, ss);
    Writeln('  • Respuesta servidor: ', http.ResponseCode, ' ', http.ResponseText);
    if Length(resp) > 0 then
      Writeln('  • Datos: ', resp);
  finally
    ss.Free;
    http.Free;
  end;
end;

procedure PostStream(const URL: string; const FilePath: string);
var
  http: TIdHTTP;
  fs: TFileStream;
  resp: string;
begin
  http := TIdHTTP.Create(nil);
  try
    http.Request.ContentType := 'application/octet-stream';
    fs := TFileStream.Create(FilePath, fmOpenRead or fmShareDenyNone);
    try
      resp := http.Post(URL, fs);
      Writeln('  • Respuesta servidor: ', http.ResponseCode, ' ', http.ResponseText);
      if Length(resp) > 0 then
        Writeln('  • Datos: ', resp);
    finally
      fs.Free;
    end;
  finally
    http.Free;
  end;
end;

// Simple helper IfThen for older compilers
function IfThen(cond: Boolean; const TrueVal, FalseVal: string): string;
begin
  if cond then
    Result := TrueVal
  else
    Result := FalseVal;
end;

procedure PrintBanner;
begin
  Writeln('╔═══════════════════════════════════════════════════╗');
  Writeln('║       HTTP CLIENT - MODO CONSOLA                  ║');
  Writeln('║       Cliente Pascal - Proyecto #2                ║');
  Writeln('║       By Alberto Caro - INFO1157                  ║');
  Writeln('╚═══════════════════════════════════════════════════╝');
  Writeln;
end;

procedure Usage;
begin
  Writeln('Usage: pas_client_send_data <server_url> <data_file>');
  Writeln('Example: pas_client_send_data http://127.0.0.1:5000 data.dat');
end;

var
  serverURL: string;
  dataFile: string;
  regs: TArray<TRegistro>;
  jsonPayload: string;
  fileSize: Int64;
  numRecords: Integer;
begin
  try
    PrintBanner;
    
    if ParamCount < 2 then
    begin
      Writeln('[ERROR] Argumentos insuficientes');
      Writeln;
      Usage;
      Halt(1);
    end;
    
    serverURL := ParamStr(1);
    dataFile := ParamStr(2);

    Writeln('[INFO] Configuración:');
    Writeln('  • Servidor: ', serverURL);
    Writeln('  • Archivo datos: ', dataFile);
    Writeln;

    if not FileExists(dataFile) then
    begin
      Writeln('[ERROR] Archivo no encontrado: ', dataFile);
      Halt(1);
    end;

    fileSize := GetFileSize(dataFile);
    numRecords := fileSize div RECORD_SIZE;
    Writeln('[INFO] Archivo cargado:');
    Writeln('  • Tamaño: ', fileSize, ' bytes');
    Writeln('  • Registros: ', numRecords);
    Writeln;

    regs := ReadLastRecords(dataFile, 10);
    if Length(regs) = 0 then
    begin
      Writeln('[ERROR] No se encontraron registros en ', dataFile);
      Halt(1);
    end;

    jsonPayload := BuildJSONPayload(regs);
    
    Writeln('[1/2] Enviando datos JSON (POST /upload-json)...');
    Writeln('  • Content-Type: application/json');
    Writeln('  • Registros: ', Length(regs));
    PostJSON(serverURL + '/upload-json', jsonPayload);
    Writeln('  ✓ JSON enviado exitosamente');
    Writeln;

    Writeln('[2/2] Enviando datos Stream (POST /upload-stream)...');
    Writeln('  • Content-Type: application/octet-stream');
    Writeln('  • Tamaño: ', fileSize, ' bytes');
    PostStream(serverURL + '/upload-stream', dataFile);
    Writeln('  ✓ Stream enviado exitosamente');
    Writeln;

    Writeln('╔═══════════════════════════════════════════════════╗');
    Writeln('║              PROCESO COMPLETADO                   ║');
    Writeln('╚═══════════════════════════════════════════════════╝');
  except
    on E: Exception do
    begin
      Writeln;
      Writeln('[ERROR] ', E.ClassName, ': ', E.Message);
      Halt(1);
    end;
  end;
end.
