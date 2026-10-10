# Gato Sphynx — Entre os Fios

Asset original modelado proceduralmente no Blender 5.1, por `scripts/build-sphynx.py`. Não usa malha de terceiros, fotografias mapeadas, geração de imagem ou pixels do vídeo incorporados.

Referência visual: o gato sem pelos que se limpa em `blink-182 — I Miss You` (2003), vídeo oficial fornecido pelo usuário, aproximadamente 00:42 e 00:45. Os frames locais de análise são `analysis/frames/0043.jpg` e `0046.jpg`, fora do site publicado.

A reconstrução busca os sinais visuais do animal: corpo magro e contínuo, tórax estreito, membros longos, cauda fina curvada, cabeça em cunha, olhos discretos amendoados, orelhas triangulares grandes e côncavas, pele marfim rosada com poros e dobras. É uma interpretação artística procedural, não uma digitalização do animal exato do vídeo.

## Reprodução

```sh
blender -b --python scripts/build-sphynx.py
```

O script reconstrói a anatomia, assa as texturas de cor e normal, monta um esqueleto simples, cria uma animação de limpeza de 8 segundos e exporta `dist/models/sphynx-v6.glb`. O `.blend` preserva a cena de trabalho e uma iluminação neutra para comparação.

- Raiz: `Sphynx`
- Clip: `Sphynx grooming • 8s`
- Bones: `body`, `head`, `paw`, `tail`
- Direção: frente -Y no Blender, +Z no glTF
- Patas apoiadas próximas de z=0 no Blender / y=0 no glTF
- Arquivo GLB autossuficiente com texturas PNG incorporadas
- `stats.json`: contagem e dimensões aproximadas

O clip movimenta cabeça, pata levantada e cauda suavemente; não desloca o root no cenário. Os limites do refinamento são a expressão esculpida à mão e o esqueleto compacto, sem músculos simulados ou língua articulada.
