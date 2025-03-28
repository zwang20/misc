/*#[derive(Debug, serde::Serialize, serde::Deserialize)]
enum FunctionalType {
    M062X,
}

#[allow(non_camel_case_types)]
#[derive(Debug, serde::Serialize, serde::Deserialize)]
enum BasisType {
    _6_31pG_D,
    def2SVP,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct QuantumMechanicsType {
    functional_type: FunctionalType,
    basis_type: BasisType,
}
*/

// manual backfilling:
// SELECT MIN(local_path + 1) FROM runs WHERE (local_path + 1) NOT IN (SELECT local_path FROM runs);
// SELECT * FROM molecules WHERE compound_id NOT IN (SELECT compound_id FROM runs) ORDER BY rotatable_bonds ASC, num_atoms ASC LIMIT 5;

// INSERT INTO runs VALUES ('mobley_6714389', 'RelaxedMinEquilGAFF', 'Received', 12, 'gadi', '/scratch/cw7/mw7780/.automated/12/');
// INSERT INTO runs VALUES ('mobley_303222', 'RelaxedMinEquilGAFF', 'Received', 13, 'gadi', '/scratch/cw7/mw7780/.automated/13/');
// python prep.py mobley_303222 13 gadi
// rsync -r data/13/ gadi:/scratch/cw7/mw7780/.automated/13/
// UPDATE runs SET status = 'Running' WHERE local_path = 13;

// INSERT INTO runs VALUES ('mobley_3867265', 'RelaxedMinEquilGAFF', 'Received', 14, 'gadi', '/scratch/cw7/mw7780/.automated/14/');
// python prep.py mobley_3867265 14 gadi
// rsync -r data/14/ gadi:/scratch/cw7/mw7780/.automated/14/
// UPDATE runs SET status = 'Running' WHERE local_path = 14;

// INSERT INTO runs VALUES ('mobley_9121449', 'RelaxedMinEquilGAFF', 'Received', 15, 'gadi', '/scratch/cw7/mw7780/.automated/15/');
// python prep.py mobley_9121449 15 gadi
// rsync -r data/15/ gadi:/scratch/cw7/mw7780/.automated/15/
// UPDATE runs SET status = 'Running' WHERE local_path = 15;

// INSERT INTO runs VALUES ('mobley_3982371', 'RelaxedMinEquilGAFF', 'Received', 16, 'gadi', '/scratch/cw7/mw7780/.automated/16/');
// python prep.py mobley_3982371 16 gadi
// rsync -r data/16/ gadi:/scratch/cw7/mw7780/.automated/16/
// UPDATE runs SET status = 'Running' WHERE local_path = 16;

// Deleting entries
// DELETE FROM runs WHERE local_path=13;

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct Molecule {
    compound_id: String,
    smiles: String,
    iupac: String,
    experimental_value: f64,
    experimental_uncertainty: f64,
    calculated_value: f64,
    calculated_uncertainty: f64,
    experimental_reference: String,
    calculated_reference: String,
    notes: Option<String>,
    rotatable_bonds: u16,
    num_atoms: u16,
}

#[derive(Debug, PartialEq, serde::Serialize, serde::Deserialize)]
enum StatusType {
    Planned,
    Running,
    Received,
    Finished,
}

#[allow(non_camel_case_types)]
#[derive(Debug, PartialEq, serde::Serialize, serde::Deserialize)]
enum RemoteHostType {
    localhost,
    katana,
    gadi,
    setonix,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
enum MolecularDynamicsRunType {
    RelaxedMinEquilGAFF,
    RelaxedForwardGAFF,
    RelaxedReversedGAFF,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct Run {
    compound_id: String,
    run_type: MolecularDynamicsRunType,
    status: StatusType,
    local_path: u16,
    remote_host: RemoteHostType,
    remote_path: String,
}

#[allow(non_snake_case)]
#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct KatanaJob {
    Job_Name: u16,
    job_state: char,
}

#[allow(non_snake_case)]
#[derive(Debug, serde::Serialize, serde::Deserialize)]
struct GadiJob {
    Job_Name: String,
    job_state: char,
}

fn update_run_status(
    local_path: u16,
    new_status: StatusType,
    connection: &rusqlite::Connection,
) -> Result<(u16, StatusType), Box<dyn std::error::Error>> {
    connection.execute(
        &format!(
            "UPDATE runs SET status = '{:?}' WHERE local_path = {}",
            new_status, local_path
        ),
        [],
    )?;
    Ok((local_path, new_status))
}

fn receive_files(
    Run {
        compound_id: _,
        run_type: _,
        status,
        local_path,
        remote_host,
        remote_path,
    }: Run,
    connection: &rusqlite::Connection,
) {
    // check if status is correct
    if status != StatusType::Running {
        return;
    }
    match std::process::Command::new("rsync")
        .arg("-r")
        .arg(format!("{:?}:{}", remote_host, remote_path))
        .arg(format!("data/{}", local_path))
        .output()
    {
        Ok(_) => println!(
            "{:?}",
            update_run_status(local_path, StatusType::Received, connection)
        ),
        Err(e) => println!("{:?}", e),
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Sleeping for 30");
    std::thread::sleep(std::time::Duration::from_secs(30));
    println!("Loading database");
    let connection = rusqlite::Connection::open("frozen_solute_model.db")?;
    let mut statement = connection.prepare("SELECT * FROM molecules")?;
    let molecules = serde_rusqlite::from_rows::<Molecule>(statement.query([])?);
    for molecule in molecules {
        molecule?;
    }

    let mut statement = connection.prepare("SELECT * FROM runs")?;
    let runs = serde_rusqlite::from_rows::<Run>(statement.query([])?);
    for run in runs {
        run?;
    }

    println!("Getting run data");
    let mut jobs: Vec<u16> = vec![];

    // katana
    {
        println!("Updating Katana");
        let katana_raw_json = std::fs::File::create("server/katana_raw.json")?;
        let output = std::process::Command::new("ssh")
            .arg("katana")
            .arg("qstat -f -F json")
            .stdout(katana_raw_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());
        let katana_json = std::fs::File::create("server/katana.json")?;
        let output = std::process::Command::new("jq")
            .arg("[.Jobs | to_entries[] | select((.value.Job_Owner | startswith(\"z5358697\")) or (.value.Job_Owner | startswith(\"z5382435\"))) | .value]")
            .arg("server/katana_raw.json")
            .stdout(katana_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());
        let output = std::process::Command::new("rm")
            .arg("server/katana_raw.json")
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());

        jobs.append(
            &mut serde_json::from_str::<Vec<KatanaJob>>(&std::fs::read_to_string("server/katana.json")?)
                .unwrap_or_default()
                .into_iter()
                .map(|i| i.Job_Name)
                .collect::<Vec<u16>>(),
        );
    }

    // gadi
    {
        println!("Updating gadi");
        let gadi_raw_json = std::fs::File::create("server/gadi_raw.json")?;
        let output = std::process::Command::new("ssh")
            .arg("gadi")
            .arg("qstat -f -F json")
            .stdout(gadi_raw_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());
        let gadi_json = std::fs::File::create("server/gadi.json")?;
        let output = std::process::Command::new("jq")
            .arg("try([.Jobs | to_entries[] | select(.value.Job_Owner | startswith(\"mw7780\")) | .value]) // []")
            .arg("server/gadi_raw.json")
            .stdout(gadi_json)
            .output();
        assert!(output.is_ok(), "{output:?}");
        assert!(output?.status.success());

        jobs.append(
            &mut serde_json::from_str::<Vec<GadiJob>>(&std::fs::read_to_string("server/gadi.json")?)
                .unwrap_or_default()
                .into_iter()
                .map(|i| i.Job_Name.parse::<u16>().unwrap())
                .collect::<Vec<u16>>(),
        );
    }

    jobs.sort_unstable(); // they are supposed to be unique anyway
    println!("Jobs: {:?}", jobs);

    let mut katana_queue_length: u8 = serde_json::from_str::<Vec<KatanaJob>>(&std::fs::read_to_string("server/katana.json")?).unwrap_or_default().into_iter().fold(0, |acc, x| acc + (x.job_state == 'Q') as u8);
    let mut gadi_queue_length: u8 = serde_json::from_str::<Vec<GadiJob>>(&std::fs::read_to_string("server/gadi.json")?).unwrap_or_default().into_iter().fold(0, |acc, x| acc + (x.job_state == 'Q') as u8);
    gadi_queue_length += 0;
    println!("gadi queue length: {}", gadi_queue_length);

    let mut planned: u8 = 0;
    let mut statement = connection.prepare("SELECT * FROM runs")?;
    let runs = serde_rusqlite::from_rows::<Run>(statement.query([])?);
    for run in runs {
        let run = run?;
        match &run.status {
            StatusType::Planned => 'match_status: {
                planned += 1;
                // just do katana for now

                if run.remote_host == RemoteHostType::localhost {
                    if katana_queue_length < 3 {
                        let output = connection.execute(
                            // TODO: do something other than katana
                            &format!(
                                "UPDATE runs SET remote_path = '/srv/scratch/z5358697/.automated/{}/', remote_host = 'katana' WHERE local_path = {}",
                                run.local_path, run.local_path
                            ),
                            [],
                        );
                        println!("pick remote host {:?}", output);

                        katana_queue_length += 1;
                        break 'match_status;
                    } else {
                        println!("katana busy, skipping");
                        break 'match_status;
                    }
                }

                let output = std::process::Command::new("python")
                    .arg("prep.py")
                    .arg(&run.compound_id)
                    .arg(run.local_path.to_string())
                    .output();
                println!("python prep.py {:?}", output);
                if output.is_err() {
                    break 'match_status;
                } else if !output?.status.success() {
                    break 'match_status;
                }

                let output = std::process::Command::new("rsync")
                    .arg("-r")
                    .arg(format!("data/{}/", run.local_path))
                    .arg(format!("{:?}:{}", run.remote_host, run.remote_path))
                    .output();
                println!("rsync copy to server {:?}", output);
                if output.is_err() {
                    break 'match_status;
                } else if !output?.status.success() {
                    break 'match_status;
                }

                let output = std::process::Command::new("ssh")
                    .arg(format!("{:?}", run.remote_host))
                    .arg(format!("cd {}; qsub {}", run.remote_path, run.local_path))
                    .output();
                println!("ssh start remote job {:?}", output);
                if output.is_err() {
                    break 'match_status;
                }

                println!(
                    "{:?}",
                    update_run_status(run.local_path, StatusType::Running, &connection)
                )
            }
            StatusType::Running => {
                if !jobs.iter().any(|name| name == &run.local_path) {
                    receive_files(run, &connection);
                }
            }
            StatusType::Received => {}
            StatusType::Finished => {}
        }
    }

    // jobs are running, no need to do anything
    // TODO: check queue status
    if planned != 0 {
        return Ok(());
    }

    println!("No planned jobs, generating");
    for _ in 0..3 {
        let mut statement = connection
            .prepare("SELECT * FROM molecules WHERE compound_id NOT IN (SELECT compound_id FROM runs) ORDER BY rotatable_bonds ASC, num_atoms ASC")?;
        let molecule = serde_rusqlite::from_rows::<Molecule>(statement.query([])?)
            .next()
            .ok_or("All done!")??;
        println!("{:?}", molecule);
        connection
            .execute(&format!("INSERT INTO runs (compound_id, run_type, status, remote_host, remote_path) VALUES ('{}', '{:?}', '{:?}', '{:?}', '{}')", molecule.compound_id, MolecularDynamicsRunType::RelaxedMinEquilGAFF, StatusType::Planned, RemoteHostType::localhost, "/dev/null/"), [])?;
    }
    Ok(())
}
