SELECT p.nompsso, p.sobnompsso, ps.conteudopost, ps.nivelvisib
FROM pessoal p
JOIN conta c
ON p.idconta = c.idconta
JOIN post ps
ON ps.idconta = c.idconta
WHERE ps.nivelvisib = 'PUBLICO';